import json
from typing import Optional
from collector.base import BaseParser, generate_deterministic_uuid
from normalization.schema import TelemetryEvent
from datetime import datetime, timezone
import dateutil.parser

class CowrieParser(BaseParser):
    def parse(self, raw_log: str) -> Optional[TelemetryEvent]:
        raw_log = raw_log.strip()
        if not raw_log:
            return None

        try:
            data = json.loads(raw_log)
        except json.JSONDecodeError:
            return None

        eventid = data.get("eventid", "")
        if not eventid.startswith("cowrie."):
            return None

        try:
            ts = dateutil.parser.parse(data.get("timestamp"))
        except:
            ts = datetime.now(timezone.utc)

        base_event = TelemetryEvent(
            event_id=generate_deterministic_uuid(raw_log),
            timestamp=ts,
            source="cowrie",
            event_type="honeypot_event",
            source_ip=data.get("src_ip"),
            source_port=data.get("src_port"),
            destination_ip=data.get("dst_ip"),
            destination_port=data.get("dst_port"),
            session_id=data.get("session"),
            username=data.get("username"),
            protocol="SSH/Telnet",
            raw_event=data
        )

        if eventid == "cowrie.session.connect":
            base_event.event_type = "honeypot_connection"
            base_event.action = "connect"
            base_event.status = "success"
        elif eventid == "cowrie.login.success":
            base_event.event_type = "honeypot_authentication"
            base_event.action = "authentication"
            base_event.status = "success"
        elif eventid == "cowrie.login.failed":
            base_event.event_type = "honeypot_authentication"
            base_event.action = "authentication"
            base_event.status = "failed"
        elif eventid == "cowrie.command.input":
            base_event.event_type = "honeypot_command"
            base_event.action = "command"
            base_event.command = data.get("input")
            base_event.status = "observed"
        elif eventid == "cowrie.session.closed":
            base_event.event_type = "session_end"
            base_event.action = "disconnect"
            base_event.status = "success"
        else:
            base_event.event_type = "honeypot_interaction"
            base_event.action = eventid
            base_event.status = "observed"

        return base_event
