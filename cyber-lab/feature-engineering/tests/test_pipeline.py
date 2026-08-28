import pytest
from datetime import datetime, timedelta, timezone
from preprocessing.cleaner import clean_events
from sessions.sessionizer import sessionize_events
from features.temporal import extract_temporal_features
from features.authentication import extract_authentication_features
from features.behavioral import compile_behavioral_features

def test_cleaner():
    raw_events = [
        {"event_id": "1", "timestamp": "2026-08-28T10:00:00Z", "source": "ssh-server", "event_type": "connect"},
        {"event_id": "2", "timestamp": "2026-08-28T10:00:00", "source": "ssh-server"} # Missing event_type
    ]
    cleaned = clean_events(raw_events)
    assert len(cleaned) == 1
    assert cleaned[0]["timestamp"].tzinfo is not None

def test_sessionizer():
    base_time = datetime(2026, 8, 28, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        {"timestamp": base_time, "source_ip": "10.0.0.1", "source": "ssh"},
        {"timestamp": base_time + timedelta(seconds=10), "source_ip": "10.0.0.1", "source": "ssh"},
        {"timestamp": base_time + timedelta(seconds=400), "source_ip": "10.0.0.1", "source": "ssh"} # > 300s timeout
    ]
    sessions = sessionize_events(events)
    assert len(sessions) == 2
    assert len(sessions[0]["events"]) == 2
    assert len(sessions[1]["events"]) == 1

def test_temporal_features():
    base_time = datetime(2026, 8, 28, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        {"timestamp": base_time},
        {"timestamp": base_time + timedelta(seconds=60)}
    ]
    feats = extract_temporal_features(events)
    assert feats["session_duration"] == 60.0
    assert feats["event_count"] == 2
    assert feats["events_per_minute"] == 2.0

def test_authentication_features():
    events = [
        {"action": "connect", "status": "failed"},
        {"action": "connect", "status": "failed"},
        {"action": "connect", "status": "success"},
        {"action": "query", "status": "success"} # Ignored for auth
    ]
    feats = extract_authentication_features(events)
    assert feats["authentication_attempts"] == 3
    assert feats["authentication_failures"] == 2
    assert feats["authentication_successes"] == 1
    assert feats["authentication_failure_rate"] == 2.0 / 3.0

def test_behavioral_compilation():
    base_time = datetime(2026, 8, 28, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        {"timestamp": base_time, "source_ip": "10.0.0.1", "source": "ssh", "action": "connect"}
    ]
    feats = compile_behavioral_features("session_1", "ip_10.0.0.1", events)
    assert feats["session_id"] == "session_1"
    assert feats["source_ip"] == "10.0.0.1"
    assert feats["behavior_sequence"] == ["ssh.connect"]
    assert "events_per_minute" in feats["feature_vector"]
