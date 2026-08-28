import os
import psycopg2
from psycopg2.extras import Json, DictCursor
import logging
from typing import List, Dict, Any

logger = logging.getLogger("storage.postgres")

class PostgresStorage:
    def __init__(self):
        self.host = os.environ.get("POSTGRES_HOST", "adaptx-db")
        self.port = os.environ.get("POSTGRES_PORT", "5432")
        self.db = os.environ.get("POSTGRES_DB", "adaptx_lab")
        self.user = os.environ.get("POSTGRES_USER", "adaptx_user")
        self.password = os.environ.get("POSTGRES_PASSWORD", "password123")
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.db,
                user=self.user,
                password=self.password
            )
            logger.info("Connected to PostgreSQL for feature storage.")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.conn = None

    def get_unprocessed_telemetry(self, limit: int = 1000) -> List[Dict[Any, Any]]:
        """
        In a real system, we'd track the last processed timestamp. 
        For Phase 1.4 verification, we will fetch everything and rely on idempotency,
        or track the max window_end processed.
        """
        if not self.conn or self.conn.closed:
            self.connect()
            if not self.conn:
                return []
                
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                # Fetch all telemetry sorted by timestamp
                # In production, we'd add `WHERE timestamp > last_processed`
                cur.execute("SELECT * FROM telemetry_events ORDER BY timestamp ASC LIMIT %s;", (limit,))
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch telemetry: {e}")
            if self.conn:
                self.conn.rollback()
            return []

    def store_features(self, feature: Dict[str, Any]) -> bool:
        if not self.conn or self.conn.closed:
            self.connect()
            if not self.conn:
                return False

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO behavioral_features (
                        feature_id, session_id, source_ip, window_start, window_end,
                        event_count, session_duration, events_per_minute,
                        unique_destinations, unique_destination_ports, unique_protocols, unique_services,
                        authentication_attempts, authentication_failures, authentication_successes, authentication_failure_rate,
                        command_count, unique_command_count, unique_resources, service_transition_count, cross_service_activity,
                        behavior_sequence, feature_vector
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s
                    ) ON CONFLICT (session_id, window_start) DO UPDATE SET
                        window_end = EXCLUDED.window_end,
                        event_count = EXCLUDED.event_count,
                        session_duration = EXCLUDED.session_duration,
                        events_per_minute = EXCLUDED.events_per_minute,
                        unique_destinations = EXCLUDED.unique_destinations,
                        unique_destination_ports = EXCLUDED.unique_destination_ports,
                        unique_protocols = EXCLUDED.unique_protocols,
                        unique_services = EXCLUDED.unique_services,
                        authentication_attempts = EXCLUDED.authentication_attempts,
                        authentication_failures = EXCLUDED.authentication_failures,
                        authentication_successes = EXCLUDED.authentication_successes,
                        authentication_failure_rate = EXCLUDED.authentication_failure_rate,
                        command_count = EXCLUDED.command_count,
                        unique_command_count = EXCLUDED.unique_command_count,
                        unique_resources = EXCLUDED.unique_resources,
                        service_transition_count = EXCLUDED.service_transition_count,
                        cross_service_activity = EXCLUDED.cross_service_activity,
                        behavior_sequence = EXCLUDED.behavior_sequence,
                        feature_vector = EXCLUDED.feature_vector;
                """, (
                    feature["feature_id"], feature["session_id"], feature["source_ip"], feature["window_start"], feature["window_end"],
                    feature["event_count"], feature["session_duration"], feature["events_per_minute"],
                    feature["unique_destinations"], feature["unique_destination_ports"], feature["unique_protocols"], feature["unique_services"],
                    feature["authentication_attempts"], feature["authentication_failures"], feature["authentication_successes"], feature["authentication_failure_rate"],
                    feature["command_count"], feature["unique_command_count"], feature["unique_resources"], feature["service_transition_count"], feature["cross_service_activity"],
                    Json(feature["behavior_sequence"]), Json(feature["feature_vector"])
                ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to insert feature: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def close(self):
        if self.conn:
            self.conn.close()
