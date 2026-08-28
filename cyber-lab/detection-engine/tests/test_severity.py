import pytest
from severity.classifier import classify_severity

def test_severity_ml_only():
    corr = {
        "triggered_rules": ["ML_SUSPICIOUS_BEHAVIOR"],
        "evidence": {"signals": [{"rule": "ML_SUSPICIOUS_BEHAVIOR", "details": {"probability": 0.85}}]}
    }
    sev, conf = classify_severity(corr)
    assert sev == "MEDIUM"
    assert 0.8 <= conf <= 0.9

def test_severity_critical():
    corr = {
        "triggered_rules": ["ML_SUSPICIOUS_BEHAVIOR", "SSH_BRUTE_FORCE"],
        "evidence": {"signals": [
            {"rule": "ML_SUSPICIOUS_BEHAVIOR", "details": {"probability": 0.9}},
            {"rule": "SSH_BRUTE_FORCE", "details": {}}
        ]}
    }
    sev, conf = classify_severity(corr)
    assert sev == "CRITICAL"
    assert conf == 1.0
