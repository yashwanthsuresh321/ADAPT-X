import re
from typing import Optional
from collector.base import BaseParser, generate_deterministic_uuid
from normalization.schema import TelemetryEvent

class SSHParser(BaseParser):
    def __init__(self):
        # Connection from 10.10.10.2 port 37255
        self.conn_pattern = re.compile(r'Connection from ([\d\.]+) port (\d+)')
        # Failed password for testuser from 10.10.10.2 port 54848
        self.auth_fail_pattern = re.compile(r'Failed password for (invalid user )?(.*?) from ([\d\.]+) port (\d+)')
        # Accepted password for testuser from 10.10.10.2 port 54848
        self.auth_success_pattern = re.compile(r'Accepted password for (.*?) from ([\d\.]+) port (\d+)')

    def parse(self, raw_log: str) -> Optional[TelemetryEvent]:
        raw_log = raw_log.strip()
        if not raw_log:
            return None

        event_id = generate_deterministic_uuid(raw_log)
        
        # Check Auth Failure
        match = self.auth_fail_pattern.search(raw_log)
        if match:
            username = match.group(2)
            source_ip = match.group(3)
            source_port = int(match.group(4))
            return TelemetryEvent(
                event_id=event_id,
                source="ssh-server",
                event_type="ssh_authentication",
                source_ip=source_ip,
                source_port=source_port,
                protocol="SSH",
                username=username,
                action="authentication",
                status="failed",
                raw_event={"raw_log": raw_log}
            )

        # Check Auth Success
        match = self.auth_success_pattern.search(raw_log)
        if match:
            username = match.group(1)
            source_ip = match.group(2)
            source_port = int(match.group(3))
            return TelemetryEvent(
                event_id=event_id,
                source="ssh-server",
                event_type="ssh_authentication",
                source_ip=source_ip,
                source_port=source_port,
                protocol="SSH",
                username=username,
                action="authentication",
                status="success",
                raw_event={"raw_log": raw_log}
            )

        # Check Connection
        match = self.conn_pattern.search(raw_log)
        if match:
            source_ip = match.group(1)
            source_port = int(match.group(2))
            return TelemetryEvent(
                event_id=event_id,
                source="ssh-server",
                event_type="ssh_connection",
                source_ip=source_ip,
                source_port=source_port,
                protocol="SSH",
                action="connect",
                status="success",
                raw_event={"raw_log": raw_log}
            )

        return None
