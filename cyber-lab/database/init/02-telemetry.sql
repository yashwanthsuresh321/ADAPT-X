-- ADAPT-X Phase 1.3
-- Telemetry events table for storing normalized logs from cyber lab services.

CREATE TABLE IF NOT EXISTS telemetry_events (
    event_id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    source VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source_ip VARCHAR(45),
    source_port INT,
    destination_ip VARCHAR(45),
    destination_port INT,
    protocol VARCHAR(20),
    username VARCHAR(100),
    session_id VARCHAR(100),
    action VARCHAR(100),
    resource TEXT,
    command TEXT,
    status VARCHAR(50),
    severity VARCHAR(20),
    raw_event JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_source ON telemetry_events(source);
CREATE INDEX IF NOT EXISTS idx_telemetry_event_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_source_ip ON telemetry_events(source_ip);
CREATE INDEX IF NOT EXISTS idx_telemetry_session_id ON telemetry_events(session_id);
