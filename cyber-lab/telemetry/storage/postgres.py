import os
import psycopg2
from psycopg2.extras import Json
import logging
from normalization.schema import TelemetryEvent

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
            logger.info("Connected to PostgreSQL for telemetry storage.")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.conn = None

    def store_event(self, event: TelemetryEvent) -> bool:
        if not self.conn or self.conn.closed:
            self.connect()
            if not self.conn:
                return False

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telemetry_events (
                        event_id, timestamp, source, event_type, source_ip, source_port,
                        destination_ip, destination_port, protocol, username, session_id,
                        action, resource, command, status, severity, raw_event, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (event_id) DO NOTHING;
                """, (
                    str(event.event_id), event.timestamp, event.source, event.event_type,
                    event.source_ip, event.source_port, event.destination_ip, event.destination_port,
                    event.protocol, event.username, event.session_id, event.action,
                    event.resource, event.command, event.status, event.severity,
                    Json(event.raw_event) if event.raw_event else None,
                    Json(event.metadata) if event.metadata else None
                ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to insert telemetry event: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def close(self):
        if self.conn:
            self.conn.close()
