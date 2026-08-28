import time
from config.settings import logger, DETECTION_INTERVAL
from storage.postgres import fetch_unprocessed_predictions, upsert_alert
from detection.correlator import correlate_signals
from severity.classifier import classify_severity
from alerts.builder import build_alert

def process_predictions():
    records = fetch_unprocessed_predictions()
    if not records:
        return 0
        
    alerts_created = 0
    for record in records:
        correlated_data = correlate_signals(record)
        
        if correlated_data and correlated_data.get("triggered_rules"):
            severity, confidence = classify_severity(correlated_data)
            alert = build_alert(record, correlated_data, severity, confidence)
            
            success = upsert_alert(alert)
            if success:
                alerts_created += 1
                logger.info(f"Upserted alert for session {record.get('session_id')} (Type: {alert['alert_type']}, Severity: {severity})")
            else:
                logger.error(f"Failed to upsert alert for session {record.get('session_id')}")
                
    return alerts_created

def main():
    logger.info("Starting ADAPT-X Detection Engine...")
    logger.info(f"Polling interval: {DETECTION_INTERVAL} seconds")
    
    while True:
        try:
            alerts_count = process_predictions()
            if alerts_count > 0:
                logger.info(f"Processed {alerts_count} new alerts.")
        except Exception as e:
            logger.error(f"Error in detection loop: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
        time.sleep(DETECTION_INTERVAL)

if __name__ == "__main__":
    main()
