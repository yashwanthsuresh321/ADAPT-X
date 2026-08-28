from config.settings import (
    SSH_BRUTE_FORCE_MIN_ATTEMPTS,
    SSH_BRUTE_FORCE_FAILURE_RATE,
    COMMAND_ACTIVITY_THRESHOLD,
    ML_SUSPICIOUS_THRESHOLD
)

def evaluate_ssh_brute_force(feature_record):
    attempts = feature_record.get('authentication_attempts', 0)
    failure_rate = feature_record.get('authentication_failure_rate', 0.0)
    
    if attempts >= SSH_BRUTE_FORCE_MIN_ATTEMPTS and failure_rate >= SSH_BRUTE_FORCE_FAILURE_RATE:
        return {
            "rule": "SSH_BRUTE_FORCE",
            "triggered": True,
            "reason": f"Observed {attempts} auth attempts with {failure_rate*100:.1f}% failure rate.",
            "evidence": {
                "attempts": attempts,
                "failures": feature_record.get('authentication_failures', 0),
                "failure_rate": failure_rate
            }
        }
    return {"triggered": False}

def evaluate_cross_service_activity(feature_record):
    is_cross = feature_record.get('cross_service_activity', False)
    unique_services = feature_record.get('unique_services', 0)
    
    if is_cross and unique_services > 1:
        return {
            "rule": "CROSS_SERVICE_ACTIVITY",
            "triggered": True,
            "reason": f"Activity spanned across {unique_services} unique services.",
            "evidence": {
                "unique_services": unique_services,
                "unique_destinations": feature_record.get('unique_destinations', 0),
                "unique_protocols": feature_record.get('unique_protocols', 0)
            }
        }
    return {"triggered": False}

def evaluate_honeypot_activity(feature_record):
    seq = feature_record.get('behavior_sequence')
    if seq and isinstance(seq, list):
        for event in seq:
            if isinstance(event, str) and 'cowrie' in event.lower():
                return {
                    "rule": "HONEYPOT_ACTIVITY",
                    "triggered": True,
                    "reason": "Traffic directed to the Cowrie honeypot.",
                    "evidence": {
                        "target": "cowrie"
                    }
                }
    return {"triggered": False}

def evaluate_suspicious_command_activity(feature_record):
    cmd_count = feature_record.get('command_count', 0)
    unique_cmds = feature_record.get('unique_command_count', 0)
    
    if cmd_count >= COMMAND_ACTIVITY_THRESHOLD:
        return {
            "rule": "SUSPICIOUS_COMMAND_ACTIVITY",
            "triggered": True,
            "reason": f"Unusual command volume: {cmd_count} total, {unique_cmds} unique.",
            "evidence": {
                "command_count": cmd_count,
                "unique_command_count": unique_cmds
            }
        }
    return {"triggered": False}

def evaluate_ml_suspicious_behavior(feature_record):
    prediction = feature_record.get('prediction', 'benign')
    probability = feature_record.get('probability', 0.0)
    
    if prediction == 'suspicious' and probability >= ML_SUSPICIOUS_THRESHOLD:
        return {
            "rule": "ML_SUSPICIOUS_BEHAVIOR",
            "triggered": True,
            "reason": f"ML model predicted suspicious with {(probability*100):.1f}% probability.",
            "evidence": {
                "prediction": prediction,
                "probability": probability,
                "model_version": feature_record.get('model_version')
            }
        }
    return {"triggered": False}

def evaluate_all_rules(feature_record):
    evaluators = [
        evaluate_ssh_brute_force,
        evaluate_cross_service_activity,
        evaluate_honeypot_activity,
        evaluate_suspicious_command_activity,
        evaluate_ml_suspicious_behavior
    ]
    
    triggered_rules = []
    for eval_func in evaluators:
        res = eval_func(feature_record)
        if res.get("triggered"):
            triggered_rules.append(res)
            
    return triggered_rules
