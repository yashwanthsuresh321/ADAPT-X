import uuid
import hashlib
from typing import Optional, Dict, Any

def generate_deterministic_uuid(raw_content: str) -> uuid.UUID:
    """Generate a UUID deterministically based on the raw log string.
    This ensures that if the collector restarts, the same log line generates
    the same event_id, allowing PostgreSQL to deduplicate via primary key.
    """
    m = hashlib.md5()
    m.update(raw_content.encode('utf-8'))
    return uuid.UUID(m.hexdigest())

class BaseParser:
    """Base parser interface"""
    def parse(self, raw_log: str) -> Optional[Any]:
        raise NotImplementedError("Parsers must implement parse()")
