from detection.rules import evaluate_all_rules

def sanitize_evidence(data):
    """Recursively remove or redact credential fields."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(secret in k_lower for secret in ['password', 'passwd', 'secret', 'token', 'private_key', 'credentials']):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_evidence(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_evidence(item) for item in data]
    else:
        return data

def correlate_signals(feature_record):
    triggered_rules = evaluate_all_rules(feature_record)
    
    if not triggered_rules:
        return None
        
    evidence = {
        "signals": []
    }
    
    for rule_res in triggered_rules:
        evidence["signals"].append({
            "type": "ml" if rule_res["rule"] == "ML_SUSPICIOUS_BEHAVIOR" else "rule",
            "rule": rule_res["rule"],
            "reason": rule_res["reason"],
            "details": rule_res["evidence"]
        })
        
    # Attempt to extract destination IP from sequence if available
    destination_ip = None
    seq = feature_record.get('behavior_sequence')
    if seq and isinstance(seq, list) and len(seq) > 0:
        for event in seq:
            if isinstance(event, dict) and event.get('destination_ip'):
                destination_ip = event.get('destination_ip')
                break
                
    return {
        "triggered_rules": [r["rule"] for r in triggered_rules],
        "evidence": sanitize_evidence(evidence),
        "destination_ip": destination_ip
    }
