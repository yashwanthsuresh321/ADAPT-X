import pytest
from alerts.deduplicator import generate_deduplication_key

def test_deduplication_deterministic():
    key1 = generate_deduplication_key("10.10.10.2", "SSH_BRUTE_FORCE", "session-123")
    key2 = generate_deduplication_key("10.10.10.2", "SSH_BRUTE_FORCE", "session-123")
    key3 = generate_deduplication_key("10.10.10.3", "SSH_BRUTE_FORCE", "session-123")
    
    assert key1 == key2
    assert key1 != key3
