import re
from typing import Optional
from collector.base import BaseParser, generate_deterministic_uuid
from normalization.schema import TelemetryEvent

class InternalParser(BaseParser):
    def __init__(self):
        # Example: INFO:     10.10.10.2:55134 - "GET /health HTTP/1.1" 200 OK
        self.uvicorn_pattern = re.compile(
            r'INFO:\s+([\d\.]+):(\d+) - "([A-Z]+) (.*) HTTP/[0-9\.]+" (\d+)'
        )

    def parse(self, raw_log: str) -> Optional[TelemetryEvent]:
        raw_log = raw_log.strip()
        if not raw_log:
            return None

        match = self.uvicorn_pattern.search(raw_log)
        if match:
            source_ip = match.group(1)
            source_port = int(match.group(2))
            method = match.group(3)
            resource = match.group(4)
            status_code = match.group(5)

            event = TelemetryEvent(
                event_id=generate_deterministic_uuid(raw_log),
                source="internal-server",
                event_type="internal_api_request",
                source_ip=source_ip,
                source_port=source_port,
                action=method,
                resource=resource,
                protocol="HTTP",
                status="success" if status_code.startswith("2") else "error",
                raw_event={"raw_log": raw_log},
                metadata={"status_code": status_code}
            )
            return event
        return None
