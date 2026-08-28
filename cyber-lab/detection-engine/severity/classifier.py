def classify_severity(correlated_data):
    """
    Determine severity and confidence based on correlated signals.
    Returns: (severity: str, confidence: float)
    """
    rules = correlated_data.get("triggered_rules", [])
    signals = correlated_data.get("evidence", {}).get("signals", [])
    
    ml_prob = 0.0
    for sig in signals:
        if sig["rule"] == "ML_SUSPICIOUS_BEHAVIOR":
            ml_prob = sig["details"].get("probability", 0.0)
            
    rule_count = len(rules)
    has_ml = "ML_SUSPICIOUS_BEHAVIOR" in rules
    has_ssh = "SSH_BRUTE_FORCE" in rules
    has_cross = "CROSS_SERVICE_ACTIVITY" in rules
    has_honeypot = "HONEYPOT_ACTIVITY" in rules
    
    # Severity Logic
    severity = "LOW"
    if rule_count >= 3 or (has_ml and has_ssh):
        severity = "CRITICAL"
    elif (has_ssh or has_cross) and has_ml:
        severity = "HIGH"
    elif has_ssh or has_cross:
        severity = "MEDIUM"
    elif has_honeypot:
        severity = "MEDIUM"
    elif has_ml:
        # ML suspicious only
        severity = "MEDIUM"
    elif rule_count > 1:
        severity = "MEDIUM"
        
    # Confidence Scoring
    # Base confidence on ML probability if present, plus boost for behavioral confirmation
    base_conf = ml_prob if has_ml else 0.5
    boost = 0.1 * (rule_count - (1 if has_ml else 0))
    
    # Specific strong indicators give higher base confidence
    if has_ssh:
        base_conf = max(base_conf, 0.8)
    if has_honeypot:
        base_conf = max(base_conf, 0.7)
        
    confidence = min(1.0, base_conf + boost)
    
    return severity, confidence
