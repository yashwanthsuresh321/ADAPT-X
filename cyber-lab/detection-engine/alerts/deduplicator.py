import hashlib

def generate_deduplication_key(source_ip, alert_type, session_id):
    """
    Generate a deterministic deduplication key.
    Using source_ip + alert_type + session_id string.
    """
    raw_key = f"{source_ip}|{alert_type}|{session_id}"
    return hashlib.md5(raw_key.encode('utf-8')).hexdigest()
