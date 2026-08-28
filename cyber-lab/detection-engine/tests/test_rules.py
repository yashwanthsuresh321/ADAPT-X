import pytest
from detection.rules import evaluate_all_rules

def test_ssh_brute_force():
    record = {
        "authentication_attempts": 10,
        "authentication_failures": 9,
        "authentication_failure_rate": 0.9,
    }
    rules = evaluate_all_rules(record)
    assert any(r["rule"] == "SSH_BRUTE_FORCE" for r in rules)

def test_ml_suspicious():
    record = {
        "prediction": "suspicious",
        "probability": 0.95
    }
    rules = evaluate_all_rules(record)
    assert any(r["rule"] == "ML_SUSPICIOUS_BEHAVIOR" for r in rules)

def test_benign_ignored():
    record = {
        "authentication_attempts": 1,
        "authentication_failures": 0,
        "authentication_failure_rate": 0.0,
        "prediction": "benign",
        "probability": 0.1
    }
    rules = evaluate_all_rules(record)
    assert len(rules) == 0
