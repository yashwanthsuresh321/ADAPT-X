import re
from typing import Optional
from collector.base import BaseParser, generate_deterministic_uuid
from normalization.schema import TelemetryEvent

class DatabaseParser(BaseParser):
    def __init__(self):
        # Example: 2026-08-28 16:38:33.456 UTC [123] LOG:  connection authorized: user=adaptx_user database=adaptx_lab
        self.auth_success = re.compile(r'connection authorized: user=([^ ]+) database=([^ ]+)')
        self.auth_fail = re.compile(r'password authentication failed for user "([^"]+)"')
        # Example: ... LOG:  statement: SELECT COUNT(*) FROM employees;
        self.statement = re.compile(r'statement: (.*)')

    def parse(self, raw_log: str) -> Optional[TelemetryEvent]:
        raw_log = raw_log.strip()
        if not raw_log:
            return None

        event_id = generate_deterministic_uuid(raw_log)

        # Authentication Success
        match = self.auth_success.search(raw_log)
        if match:
            return TelemetryEvent(
                event_id=event_id,
                source="database",
                event_type="database_connection",
                protocol="PostgreSQL",
                username=match.group(1),
                resource=match.group(2),
                action="connect",
                status="success",
                raw_event={"raw_log": raw_log}
            )

        # Authentication Failure
        match = self.auth_fail.search(raw_log)
        if match:
            return TelemetryEvent(
                event_id=event_id,
                source="database",
                event_type="database_connection",
                protocol="PostgreSQL",
                username=match.group(1),
                action="connect",
                status="failed",
                raw_event={"raw_log": raw_log}
            )

        # Statement
        match = self.statement.search(raw_log)
        if match:
            return TelemetryEvent(
                event_id=event_id,
                source="database",
                event_type="database_activity",
                protocol="PostgreSQL",
                command=match.group(1),
                action="query",
                status="success",
                raw_event={"raw_log": raw_log}
            )

        return None
