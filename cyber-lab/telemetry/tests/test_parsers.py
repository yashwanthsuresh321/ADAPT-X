import pytest
from collector.web import WebParser
from collector.internal import InternalParser
from collector.ssh import SSHParser
from collector.database import DatabaseParser
from collector.cowrie import CowrieParser

def test_web_parser():
    parser = WebParser()
    log = 'INFO:     10.10.10.2:55134 - "GET /health HTTP/1.1" 200 OK'
    event = parser.parse(log)
    assert event is not None
    assert event.source == "web-server"
    assert event.event_type == "http_request"
    assert event.action == "GET"
    assert event.resource == "/health"
    assert event.status == "success"
    
    # Malformed
    assert parser.parse("Malformed log line") is None

def test_internal_parser():
    parser = InternalParser()
    log = 'INFO:     127.0.0.1:35028 - "POST /api/v1/data HTTP/1.1" 404 Not Found'
    event = parser.parse(log)
    assert event is not None
    assert event.source == "internal-server"
    assert event.event_type == "internal_api_request"
    assert event.action == "POST"
    assert event.resource == "/api/v1/data"
    assert event.status == "error"

def test_ssh_parser():
    parser = SSHParser()
    
    conn_log = 'Connection from 10.10.10.2 port 37255'
    event1 = parser.parse(conn_log)
    assert event1 is not None
    assert event1.event_type == "ssh_connection"
    
    fail_log = 'Failed password for testuser from 10.10.10.2 port 54848 ssh2'
    event2 = parser.parse(fail_log)
    assert event2 is not None
    assert event2.event_type == "ssh_authentication"
    assert event2.status == "failed"
    assert event2.username == "testuser"
    
    succ_log = 'Accepted password for testuser from 10.10.10.2 port 54848 ssh2'
    event3 = parser.parse(succ_log)
    assert event3 is not None
    assert event3.event_type == "ssh_authentication"
    assert event3.status == "success"
    assert event3.username == "testuser"

def test_database_parser():
    parser = DatabaseParser()
    
    conn_log = '2026-08-28 16:38:33.456 UTC [123] LOG:  connection authorized: user=adaptx_user database=adaptx_lab application_name=psql'
    event1 = parser.parse(conn_log)
    assert event1 is not None
    assert event1.event_type == "database_connection"
    assert event1.status == "success"
    
    fail_log = '2026-08-28 16:38:33.456 UTC [123] FATAL:  password authentication failed for user "invalid_user"'
    event2 = parser.parse(fail_log)
    assert event2 is not None
    assert event2.event_type == "database_connection"
    assert event2.status == "failed"
    assert event2.username == "invalid_user"
    
    query_log = '2026-08-28 16:38:33.456 UTC [123] LOG:  statement: SELECT COUNT(*) FROM employees;'
    event3 = parser.parse(query_log)
    assert event3 is not None
    assert event3.event_type == "database_activity"
    assert event3.action == "query"

def test_cowrie_parser():
    parser = CowrieParser()
    
    # Connection
    conn_json = '{"eventid": "cowrie.session.connect", "timestamp": "2026-08-28T16:38:17.271037Z", "src_ip": "10.10.10.2", "session": "10fcff9bff1f"}'
    event1 = parser.parse(conn_json)
    assert event1 is not None
    assert event1.event_type == "honeypot_connection"
    assert event1.action == "connect"
    
    # Auth failed
    auth_json = '{"eventid": "cowrie.login.failed", "timestamp": "2026-08-28T16:38:17.271037Z", "src_ip": "10.10.10.2", "username": "root"}'
    event2 = parser.parse(auth_json)
    assert event2 is not None
    assert event2.event_type == "honeypot_authentication"
    assert event2.status == "failed"
    
    # Command
    cmd_json = '{"eventid": "cowrie.command.input", "timestamp": "2026-08-28T16:38:17.271037Z", "input": "whoami"}'
    event3 = parser.parse(cmd_json)
    assert event3 is not None
    assert event3.event_type == "honeypot_command"
    assert event3.command == "whoami"
    
    # Malformed JSON
    assert parser.parse("{malformed_json") is None
    
    # Unknown eventid
    unk_json = '{"eventid": "something.else", "timestamp": "2026-08-28T16:38:17.271037Z"}'
    event4 = parser.parse(unk_json)
    assert event4 is None
