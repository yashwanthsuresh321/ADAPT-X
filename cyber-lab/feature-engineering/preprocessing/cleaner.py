from typing import List, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger("preprocessing.cleaner")

def clean_events(raw_events: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Validates required fields, forces UTC timezone awareness, and fills missing ports/values logically.
    """
    cleaned = []
    for event in raw_events:
        try:
            # Validate required
            if not event.get("event_id") or not event.get("timestamp") or not event.get("source") or not event.get("event_type"):
                logger.warning(f"Dropping event missing required fields: {event}")
                continue
                
            # Normalize timestamp to UTC aware
            ts = event["timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            event["timestamp"] = ts
            
            # Missing source_ip default to empty string, not None, to help grouping
            event["source_ip"] = event.get("source_ip") or ""
            
            # Fill missing ports as 0 logically if None
            event["source_port"] = event.get("source_port") or 0
            event["destination_port"] = event.get("destination_port") or 0
            event["destination_ip"] = event.get("destination_ip") or ""
            
            # Fill string fields logically
            event["protocol"] = event.get("protocol") or ""
            event["username"] = event.get("username") or ""
            event["session_id"] = event.get("session_id") or ""
            event["action"] = event.get("action") or ""
            event["resource"] = event.get("resource") or ""
            event["command"] = event.get("command") or ""
            event["status"] = event.get("status") or ""
            event["severity"] = event.get("severity") or ""
            
            cleaned.append(event)
        except Exception as e:
            logger.error(f"Error cleaning event {event.get('event_id', 'unknown')}: {e}")
            
    return cleaned
