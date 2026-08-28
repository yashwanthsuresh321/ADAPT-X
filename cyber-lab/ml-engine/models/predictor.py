import joblib
import pandas as pd
import logging
import os
from data.builder import prepare_feature_vectors
from features.selector import select_features

logger = logging.getLogger("models.predictor")

class Predictor:
    def __init__(self, artifact_path: str = "artifacts/model.joblib"):
        self.artifact_path = artifact_path
        self.artifact = None
        
        if os.path.exists(self.artifact_path):
            self.artifact = joblib.load(self.artifact_path)
            logger.info(f"Loaded model artifact version: {self.artifact['model_version']}")
        else:
            logger.error(f"Model artifact not found at {self.artifact_path}")
            
    def is_loaded(self):
        return self.artifact is not None
        
    def predict(self, feature_record: dict) -> dict:
        """
        Accepts a single behavioral feature record dictionary.
        Returns the prediction dict.
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded.")
            
        # Wrap in dataframe
        # We need a 'label' column purely to make prepare_feature_vectors happy, even if None
        feature_record_copy = feature_record.copy()
        if 'label' not in feature_record_copy:
            feature_record_copy['label'] = None
            
        df = pd.DataFrame([feature_record_copy])
        flat_df = prepare_feature_vectors(df)
        X_raw = select_features(flat_df)
        
        # Ensure schema matches exactly
        schema = self.artifact['feature_schema']
        
        # Add missing columns with 0, drop extra columns
        for col in schema:
            if col not in X_raw.columns:
                X_raw[col] = 0.0
                
        X_raw = X_raw[schema] # Deterministic order
        
        # Transform
        pipeline = self.artifact['preprocessing']
        X_proc = pipeline.transform(X_raw)
        
        # Predict
        model = self.artifact['model']
        prediction = model.predict(X_proc)[0]
        
        # Probability
        probability = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_proc)[0]
            class_idx = list(model.classes_).index(prediction)
            probability = float(probs[class_idx])
            
        # Top contributing features for this prediction (naive global importance for now)
        # For true local interpretability we'd use SHAP, but feature_importances_ is fine for Phase 1.5 baseline
        importances = model.feature_importances_
        feat_imp = sorted(zip(schema, importances), key=lambda x: x[1], reverse=True)
        top_features = [{"feature": f, "value": imp} for f, imp in feat_imp[:5]]
        
        return {
            "feature_id": feature_record.get("feature_id"),
            "session_id": feature_record.get("session_id"),
            "prediction": str(prediction),
            "probability": probability,
            "model_version": self.artifact["model_version"],
            "top_features": top_features
        }
