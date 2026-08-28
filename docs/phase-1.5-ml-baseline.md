# ADAPT-X Phase 1.5 - ML Behavioral Baseline Report

## 1. Objective
The objective of Phase 1.5 is to establish a verifiable AI/ML baseline for predicting malicious behavior in the ADAPT-X cyber lab environment based on the structured behavioral features extracted in Phase 1.4.

## 2. Architecture
The ML architecture leverages a dedicated `ml-engine` service running on IP `10.10.10.80`. It retrieves `behavioral_features` from PostgreSQL, joins them with synthetic ground truth scenarios, builds a structured dataset, preprocesses features (imputation and scaling), and trains a `RandomForestClassifier`. The resulting artifact is persisted and used for deterministic inference.

## 3. Dataset Generation
Because the initial lab environments lack sufficient native ground truth, a dataset builder mechanism was implemented to deterministically map time-windows of lab activity to `ml_scenarios` with known labels.

## 4. Scenario Definitions
- `benign_web`: Background lab noise simulating standard web-server interaction.
- `ssh_bruteforce`: Bursty, high-volume authentication failures against the SSH server.
- `benign_internal`: Standard inter-service communication within the lab network.

## 5. Label Methodology
Features are labeled by performing a temporal intersection between the `window_start` and `window_end` of a `behavioral_feature` and the bounding time window of a known `ml_scenario`. Ambiguous overlaps are discarded to prevent label contamination.

## 6. Number of Samples
Total samples available for training/validation in this baseline: **6**
*(Note: As expected for an initial isolated lab environment, the sample size is extremely small. The focus of this baseline is on verifying the end-to-end mathematical pipeline rather than achieving generalized performance.)*

## 7. Feature Count
Total features utilized in the final vector schema: **17**

## 8. Class Distribution
- **Benign**: 5 samples
- **Suspicious**: 1 sample

## 9. Train/Validation/Test Split
Due to the dataset having fewer than 10 samples, a strict temporal split would leave empty datasets and cause errors. To validate the pipeline execution safely, the dataset was duplicated across Train, Validation, and Test.

## 10. Model Configuration
- **Algorithm**: `RandomForestClassifier`
- **n_estimators**: 100
- **class_weight**: 'balanced'
- **random_state**: 42

## 11-15. Metrics
*Warning: Due to dataset duplication necessary to run the pipeline on 6 samples, these metrics represent extreme overfitting and serve only to prove the mathematical pipeline functions end-to-end.*
- **Accuracy**: 1.0000
- **Precision**: 1.0000
- **Recall**: 1.0000
- **F1 Score**: 1.0000
- **ROC-AUC**: 1.0000

## 16. Confusion Matrix
```
[[5 0]
 [0 1]]
```

## 17. Feature Importance
Top 5 contributing features for the Random Forest model:
1. `session_duration`: 0.2968
2. `events_per_minute`: 0.2714
3. `service_transition_count`: 0.1026
4. `unique_services`: 0.0613
5. `authentication_successes`: 0.0481

## 18. Example Inference
```json
{
  "feature_id": "050fdb4a-f429-56fc-8c39-06ec1c842665",
  "prediction": "benign",
  "probability": 0.87,
  "model_version": "rf_baseline_20260828174015",
  "top_features": [
    {"feature": "session_duration", "value": 0.2968},
    {"feature": "events_per_minute", "value": 0.2714}
  ]
}
```

## 19. Reproducibility
The pipeline executes deterministically due to fixed random states, deterministic feature sorting `reindex(sorted(columns))`, and idempotent `ON CONFLICT` constraints in PostgreSQL. A rerun of the pipeline produces identical metrics and feature importances.

## 20. Limitations
The primary limitation is the lack of real volume in the isolated cyber lab. The model cannot generalize until Phase 1.6 or beyond generates large quantities of diverse attack traffic (e.g. via Kali Linux).

## 21. Security Considerations
- The ML Engine operates entirely within the isolated `adaptx_network` (`10.10.10.80`).
- No ports are exposed publicly.
- The engine does not have access to the Docker socket.
- The pipeline does not store raw passwords; only metadata such as `authentication_failures`.
