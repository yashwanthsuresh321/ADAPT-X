import os
import psycopg2
import pandas as pd
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("data.loader")

class PostgresLoader:
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
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.conn = None

    def load_behavioral_features(self) -> pd.DataFrame:
        if not self.conn or self.conn.closed:
            self.connect()
        try:
            query = "SELECT * FROM behavioral_features ORDER BY window_start ASC;"
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            logger.error(f"Error loading behavioral features: {e}")
            return pd.DataFrame()

    def load_scenarios(self) -> pd.DataFrame:
        if not self.conn or self.conn.closed:
            self.connect()
        try:
            query = "SELECT * FROM ml_scenarios ORDER BY window_start ASC;"
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            logger.error(f"Error loading ml scenarios: {e}")
            return pd.DataFrame()
            
    def save_prediction(self, feature_id: str, session_id: str, model_version: str, prediction: str, probability: float, top_features: str) -> bool:
        if not self.conn or self.conn.closed:
            self.connect()
        try:
            import uuid
            prediction_id = str(uuid.uuid4())
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ml_predictions (
                        prediction_id, feature_id, session_id, model_version, prediction, probability, top_features
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT ON CONSTRAINT unique_prediction DO UPDATE SET
                        prediction = EXCLUDED.prediction,
                        probability = EXCLUDED.probability,
                        top_features = EXCLUDED.top_features,
                        predicted_at = NOW();
                """, (prediction_id, feature_id, session_id, model_version, prediction, probability, top_features))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save prediction: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def close(self):
        if self.conn:
            self.conn.close()
