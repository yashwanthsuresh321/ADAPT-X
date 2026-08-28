import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class TelemetryEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str
    event_type: str
    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    command: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    raw_event: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
