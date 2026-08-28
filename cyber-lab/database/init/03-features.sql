CREATE TABLE IF NOT EXISTS behavioral_features (
    feature_id UUID PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    source_ip VARCHAR(45),
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    
    event_count INTEGER NOT NULL DEFAULT 0,
    session_duration DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    events_per_minute DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    
    unique_destinations INTEGER NOT NULL DEFAULT 0,
    unique_destination_ports INTEGER NOT NULL DEFAULT 0,
    unique_protocols INTEGER NOT NULL DEFAULT 0,
    unique_services INTEGER NOT NULL DEFAULT 0,
    
    authentication_attempts INTEGER NOT NULL DEFAULT 0,
    authentication_failures INTEGER NOT NULL DEFAULT 0,
    authentication_successes INTEGER NOT NULL DEFAULT 0,
    authentication_failure_rate DOUBLE PRECISION,
    
    command_count INTEGER NOT NULL DEFAULT 0,
    unique_command_count INTEGER NOT NULL DEFAULT 0,
    
    unique_resources INTEGER NOT NULL DEFAULT 0,
    service_transition_count INTEGER NOT NULL DEFAULT 0,
    cross_service_activity BOOLEAN NOT NULL DEFAULT FALSE,
    
    behavior_sequence JSONB,
    feature_vector JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_session_window UNIQUE (session_id, window_start)
);

CREATE INDEX IF NOT EXISTS idx_behavioral_session_id ON behavioral_features(session_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_window_start ON behavioral_features(window_start);
CREATE INDEX IF NOT EXISTS idx_behavioral_source_ip ON behavioral_features(source_ip);
