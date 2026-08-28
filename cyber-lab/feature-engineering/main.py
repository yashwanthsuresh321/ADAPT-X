import time
import os
import logging
from storage.postgres import PostgresStorage
from preprocessing.cleaner import clean_events
from sessions.sessionizer import sessionize_events
from features.behavioral import compile_behavioral_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("feature-engineering")

def process_batch():
    logger.info("Starting feature engineering batch...")
    storage = PostgresStorage()
    
    # 1. Fetch raw telemetry
    raw_events = storage.get_unprocessed_telemetry(limit=10000)
    if not raw_events:
        logger.info("No telemetry events to process.")
        storage.close()
        return
        
    logger.info(f"Fetched {len(raw_events)} telemetry events.")
    
    # 2. Preprocess & Clean
    cleaned_events = clean_events(raw_events)
    logger.info(f"Cleaned events: {len(cleaned_events)}")
    
    # 3. Sessionization
    sessions = sessionize_events(cleaned_events)
    logger.info(f"Generated {len(sessions)} sessions/windows.")
    
    # 4. Feature Extraction & Storage
    inserted_count = 0
    for session in sessions:
        group_key = session["group_key"]
        events = session["events"]
        
        # Determine session_id
        session_id = None
        if group_key.startswith("sid_"):
            session_id = group_key[4:]
            
        feature_record = compile_behavioral_features(session_id, group_key, events)
        
        if feature_record:
            success = storage.store_features(feature_record)
            if success:
                inserted_count += 1
                
    logger.info(f"Successfully upserted {inserted_count} feature records.")
    storage.close()

if __name__ == "__main__":
    logger.info("Initializing Feature Engineering Service...")
    poll_interval = int(os.environ.get("FEATURE_POLL_INTERVAL_SECONDS", "30"))
    
    # For one-shot execution or test environments:
    run_once = os.environ.get("FEATURE_RUN_ONCE", "false").lower() == "true"
    
    if run_once:
        process_batch()
    else:
        while True:
            process_batch()
            logger.info(f"Sleeping for {poll_interval} seconds...")
            time.sleep(poll_interval)
