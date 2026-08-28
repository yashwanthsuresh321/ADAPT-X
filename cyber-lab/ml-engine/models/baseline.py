from sklearn.ensemble import RandomForestClassifier

def get_baseline_model() -> RandomForestClassifier:
    """
    Returns the configured baseline Random Forest model.
    Fixed random_state for reproducibility.
    """
    return RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced'
    )
