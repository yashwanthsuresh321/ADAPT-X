CREATE TABLE IF NOT EXISTS alerts (
    alert_id UUID PRIMARY KEY,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    session_id VARCHAR(100),
    feature_id UUID REFERENCES behavioral_features(feature_id),
    prediction_id UUID,
    
    alert_type VARCHAR(100) NOT NULL,
    detection_rule VARCHAR(100) NOT NULL,
    
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'ACKNOWLEDGED', 'RESOLVED')),
    
    ml_prediction VARCHAR(50),
    ml_probability DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    
    title TEXT NOT NULL,
    description TEXT,
    
    evidence JSONB,
    behavior_sequence JSONB,
    feature_snapshot JSONB,
    
    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    
    deduplication_key VARCHAR(255) NOT NULL,
    model_version VARCHAR(100),
    
    CONSTRAINT unique_deduplication_key UNIQUE (deduplication_key)
);

CREATE INDEX IF NOT EXISTS idx_alerts_source_ip ON alerts(source_ip);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_last_seen ON alerts(last_seen);
