CREATE TABLE IF NOT EXISTS ml_scenarios (
    scenario_id VARCHAR(50) PRIMARY KEY,
    scenario_type VARCHAR(100) NOT NULL,
    label VARCHAR(20) NOT NULL CHECK (label IN ('benign', 'suspicious')),
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ml_scenarios_time ON ml_scenarios(window_start, window_end);

CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id UUID PRIMARY KEY,
    feature_id UUID NOT NULL REFERENCES behavioral_features(feature_id),
    session_id VARCHAR(100),
    model_version VARCHAR(100) NOT NULL,
    prediction VARCHAR(50) NOT NULL,
    probability DOUBLE PRECISION,
    top_features JSONB,
    predicted_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_prediction UNIQUE (feature_id, model_version)
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_feature ON ml_predictions(feature_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_time ON ml_predictions(predicted_at);
