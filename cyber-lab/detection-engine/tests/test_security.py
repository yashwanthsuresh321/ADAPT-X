import pytest
from detection.correlator import sanitize_evidence

def test_sanitize_credentials():
    raw_evidence = {
        "user": "admin",
        "password": "supersecretpassword",
        "details": {
            "token": "abcdef12345",
            "count": 5
        }
    }
    
    sanitized = sanitize_evidence(raw_evidence)
    
    assert sanitized["user"] == "admin"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["details"]["token"] == "[REDACTED]"
    assert sanitized["details"]["count"] == 5
