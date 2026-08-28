import psycopg2
import psycopg2.extras
import json
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, logger

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def fetch_unprocessed_predictions():
    query = """
    SELECT 
        p.prediction_id, p.feature_id, p.prediction, p.probability, p.model_version,
        f.session_id, f.source_ip, f.window_start, f.window_end,
        f.event_count, f.session_duration, f.events_per_minute,
        f.unique_destinations, f.unique_destination_ports, f.unique_protocols, f.unique_services,
        f.authentication_attempts, f.authentication_failures, f.authentication_successes, f.authentication_failure_rate,
        f.command_count, f.unique_command_count,
        f.cross_service_activity, f.behavior_sequence
    FROM ml_predictions p
    JOIN behavioral_features f ON p.feature_id = f.feature_id
    WHERE NOT EXISTS (
        SELECT 1 FROM alerts a WHERE a.prediction_id = p.prediction_id
    )
    ORDER BY p.predicted_at ASC
    LIMIT 100;
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return []

def upsert_alert(alert_data):
    query = """
    INSERT INTO alerts (
        alert_id, source_ip, destination_ip, session_id, feature_id, prediction_id,
        alert_type, detection_rule, severity, status,
        ml_prediction, ml_probability, confidence,
        title, description, evidence, behavior_sequence, feature_snapshot,
        first_seen, last_seen, occurrence_count, deduplication_key, model_version
    ) VALUES (
        %(alert_id)s, %(source_ip)s, %(destination_ip)s, %(session_id)s, %(feature_id)s, %(prediction_id)s,
        %(alert_type)s, %(detection_rule)s, %(severity)s, %(status)s,
        %(ml_prediction)s, %(ml_probability)s, %(confidence)s,
        %(title)s, %(description)s, %(evidence)s, %(behavior_sequence)s, %(feature_snapshot)s,
        %(first_seen)s, %(last_seen)s, %(occurrence_count)s, %(deduplication_key)s, %(model_version)s
    )
    ON CONFLICT (deduplication_key) DO UPDATE SET
        occurrence_count = alerts.occurrence_count + 1,
        last_seen = EXCLUDED.last_seen,
        updated_at = NOW(),
        prediction_id = EXCLUDED.prediction_id,
        feature_id = EXCLUDED.feature_id,
        evidence = EXCLUDED.evidence,
        feature_snapshot = EXCLUDED.feature_snapshot
    """
    try:
        # Convert dict to JSON string for jsonb columns
        for col in ['evidence', 'behavior_sequence', 'feature_snapshot']:
            if isinstance(alert_data.get(col), dict) or isinstance(alert_data.get(col), list):
                alert_data[col] = json.dumps(alert_data[col])
                
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, alert_data)
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error upserting alert: {e}")
        return False
