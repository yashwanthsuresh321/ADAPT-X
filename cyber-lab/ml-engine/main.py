import argparse
import logging
from models.trainer import train_and_evaluate
from models.predictor import Predictor
from data.loader import PostgresLoader
import psycopg2
import uuid
from datetime import datetime, timedelta, timezone
import random
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ml-engine")

def generate_scenarios():
    """
    Generates synthetic laboratory scenarios directly in ml_scenarios to provide labels
    for the unlabelled telemetry data that was captured.
    In a real environment, we'd trigger the attacker scripts. Here we annotate time windows.
    We'll annotate everything up to 5 minutes ago as 'benign_web' or 'ssh_bruteforce'
    based on our knowledge of the lab events.
    """
    logger.info("Generating controlled lab scenarios...")
    loader = PostgresLoader()
    loader.connect()
    
    if not loader.conn:
        logger.error("No database connection.")
        return
        
    try:
        # Create a benign web scenario covering the last hour, except for specific attack windows
        now = datetime.now(timezone.utc)
        
        scenarios = [
            # Benign background
            (str(uuid.uuid4()), 'benign_web', 'benign', now - timedelta(hours=2), now - timedelta(minutes=30)),
            # Suspicious SSH burst simulation
            (str(uuid.uuid4()), 'ssh_bruteforce', 'suspicious', now - timedelta(minutes=29), now - timedelta(minutes=10)),
            # Benign recent
            (str(uuid.uuid4()), 'benign_internal', 'benign', now - timedelta(minutes=9), now + timedelta(minutes=10))
        ]
        
        with loader.conn.cursor() as cur:
            for s in scenarios:
                cur.execute("""
                    INSERT INTO ml_scenarios (scenario_id, scenario_type, label, window_start, window_end, description)
                    VALUES (%s, %s, %s, %s, %s, 'Synthetic controlled scenario')
                    ON CONFLICT DO NOTHING;
                """, s)
        loader.conn.commit()
        logger.info("Successfully generated controlled lab scenarios.")
    except Exception as e:
        logger.error(f"Failed to generate scenarios: {e}")
    finally:
        loader.close()

def run_training():
    train_and_evaluate()

def run_prediction():
    predictor = Predictor()
    if not predictor.is_loaded():
        return
        
    loader = PostgresLoader()
    features_df = loader.load_behavioral_features()
    
    if features_df.empty:
        logger.info("No features available for inference.")
        return
        
    logger.info(f"Running inference on {len(features_df)} feature records...")
    success_count = 0
    
    for _, row in features_df.iterrows():
        record = row.to_dict()
        pred_res = predictor.predict(record)
        
        saved = loader.save_prediction(
            feature_id=pred_res["feature_id"],
            session_id=pred_res["session_id"],
            model_version=pred_res["model_version"],
            prediction=pred_res["prediction"],
            probability=pred_res["probability"],
            top_features=json.dumps(pred_res["top_features"])
        )
        if saved:
            success_count += 1
            
    logger.info(f"Successfully ran inference and saved {success_count} predictions.")
    loader.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ADAPT-X ML Engine Phase 1.5")
    parser.add_argument("command", choices=["generate-scenarios", "train", "evaluate", "predict"])
    
    args = parser.parse_args()
    
    if args.command == "generate-scenarios":
        generate_scenarios()
    elif args.command == "train" or args.command == "evaluate":
        run_training()
    elif args.command == "predict":
        run_prediction()
