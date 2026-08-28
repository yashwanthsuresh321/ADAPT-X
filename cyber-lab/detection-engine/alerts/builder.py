import uuid
from datetime import datetime
from alerts.deduplicator import generate_deduplication_key

def build_alert(feature_record, correlated_data, severity, confidence):
    """
    Construct the final alert dictionary for insertion into the database.
    """
    primary_rule = correlated_data["triggered_rules"][0] if correlated_data["triggered_rules"] else "ANOMALOUS_BEHAVIOR"
    
    # Determine alert_type conceptually based on primary rule
    alert_type = primary_rule
    
    source_ip = feature_record.get('source_ip', 'unknown')
    session_id = feature_record.get('session_id', 'unknown')
    
    # Extract destination IP from correlated data or sequence
    dest_ip = correlated_data.get('destination_ip')
    
    dedup_key = generate_deduplication_key(source_ip, alert_type, session_id)
    
    # Build title and description
    title = f"Suspicious Activity Detected: {alert_type.replace('_', ' ').title()}"
    description = f"Detection engine triggered {len(correlated_data['triggered_rules'])} rule(s) indicating potential malicious activity from {source_ip}."
    if "ML_SUSPICIOUS_BEHAVIOR" in correlated_data["triggered_rules"]:
        description += " The ML model also classified the activity as suspicious."
        
    return {
        "alert_id": str(uuid.uuid4()),
        "source_ip": source_ip,
        "destination_ip": dest_ip,
        "session_id": session_id,
        "feature_id": feature_record.get('feature_id'),
        "prediction_id": feature_record.get('prediction_id'),
        "alert_type": alert_type,
        "detection_rule": primary_rule,
        "severity": severity,
        "status": "NEW",
        "ml_prediction": feature_record.get('prediction'),
        "ml_probability": feature_record.get('probability'),
        "confidence": confidence,
        "title": title,
        "description": description,
        "evidence": correlated_data["evidence"],
        "behavior_sequence": feature_record.get('behavior_sequence'),
        "feature_snapshot": {
            "event_count": feature_record.get('event_count'),
            "session_duration": feature_record.get('session_duration'),
            "authentication_attempts": feature_record.get('authentication_attempts'),
            "authentication_failures": feature_record.get('authentication_failures'),
            "command_count": feature_record.get('command_count')
        },
        "first_seen": feature_record.get('window_start'),
        "last_seen": feature_record.get('window_end'),
        "occurrence_count": 1,
        "deduplication_key": dedup_key,
        "model_version": feature_record.get('model_version')
    }
