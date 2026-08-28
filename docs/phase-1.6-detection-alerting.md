# ADAPT-X Phase 1.6 — Detection & Alerting Engine

## Overview

The Detection & Alerting Engine is responsible for consuming Behavioral Features (from Phase 1.4) and ML Predictions (from Phase 1.5), running them through rule-based and behavioral classifiers, and generating actionable Security Alerts. 

It implements a hybrid approach, correlating known attack signatures with AI/ML behavioral anomalies to produce high-confidence alerts, minimizing false positives.

## Architecture

The Detection Engine runs as a standalone Python service (`adaptx-detection-engine` at `10.10.10.90`). It polls the `ml_predictions` table for new predictions that have not yet been evaluated for alerts.

1. **Storage Polling**: Fetches unprocessed `ml_predictions` joined with their corresponding `behavioral_features`.
2. **Rule Evaluation**: Applies deterministic rules (e.g. `SSH_BRUTE_FORCE`, `CROSS_SERVICE_ACTIVITY`, `HONEYPOT_ACTIVITY`, `SUSPICIOUS_COMMAND_ACTIVITY`).
3. **Correlation**: Combines all triggered deterministic rules along with the `ML_SUSPICIOUS_BEHAVIOR` model prediction. 
4. **Severity Classification**: Calculates severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and confidence based on the combinations of triggered signals.
5. **Sanitization**: Recursively redacts sensitive data (like passwords, keys) from the evidence object to prevent credentials from bleeding into security alerts.
6. **Deduplication**: Generates a deterministic `deduplication_key` based on `(source_ip, alert_type, session_id)` to deduplicate multiple instances of the same alert across time.
7. **Upsert**: Stores the final alert in the PostgreSQL `alerts` table.

## Database Schema

The `alerts` table schema includes fields such as:
- `alert_id` (UUID)
- `source_ip`, `destination_ip`, `session_id`
- `alert_type`, `detection_rule`
- `severity`, `status`
- `ml_prediction`, `ml_probability`, `confidence`
- `title`, `description`
- `evidence`, `behavior_sequence`, `feature_snapshot` (all stored as JSONB and sanitized)
- `occurrence_count`, `deduplication_key`

## Validation

Verification confirms that:
- The detection-engine container runs properly and is connected to the DB.
- The `alerts` table schema is correctly provisioned.
- Alerts are correctly generated for suspicious traffic (like SSH Brute Force and Cowrie honeypot traffic).
- Deduplication keys successfully condense duplicate alerts.
- Secrets are properly sanitized from alert evidence payloads.
