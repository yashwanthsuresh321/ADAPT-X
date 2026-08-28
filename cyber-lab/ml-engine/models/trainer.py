import pandas as pd
import joblib
from datetime import datetime, timezone
import logging
import os

from data.loader import PostgresLoader
from data.builder import build_labeled_dataset, prepare_feature_vectors
from data.splitter import split_dataset
from features.selector import select_features
from features.transformer import build_preprocessing_pipeline
from models.baseline import get_baseline_model
from models.evaluator import evaluate_model

logger = logging.getLogger("models.trainer")

def train_and_evaluate():
    logger.info("Starting ML Training Pipeline...")
    
    loader = PostgresLoader()
    features_df = loader.load_behavioral_features()
    scenarios_df = loader.load_scenarios()
    loader.close()
    
    if features_df.empty or scenarios_df.empty:
        logger.error("Insufficient data to train model.")
        return
        
    dataset = build_labeled_dataset(features_df, scenarios_df)
    if dataset.empty:
        logger.error("Labeled dataset is empty.")
        return
        
    flat_df = prepare_feature_vectors(dataset)
    
    # Split chronologically
    train_df, val_df, test_df = split_dataset(flat_df)
    
    # Select numeric features
    X_train_raw = select_features(train_df)
    y_train = train_df['label']
    
    X_val_raw = select_features(val_df)
    y_val = val_df['label']
    
    X_test_raw = select_features(test_df)
    y_test = test_df['label']
    
    # Feature Schema
    feature_schema = list(X_train_raw.columns)
    
    # Build and Fit Preprocessing on TRAIN ONLY
    pipeline = build_preprocessing_pipeline()
    X_train_proc = pipeline.fit_transform(X_train_raw)
    X_val_proc = pipeline.transform(X_val_raw) if not X_val_raw.empty else None
    X_test_proc = pipeline.transform(X_test_raw) if not X_test_raw.empty else None
    
    # Train Model
    model = get_baseline_model()
    model.fit(X_train_proc, y_train)
    
    # Evaluate
    logger.info("=== EVALUATION ON TEST SET ===")
    evaluate_model(model, X_test_proc, y_test, feature_schema)
    
    # Package Artifact
    artifact = {
        "model_version": f"rf_baseline_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "feature_schema": feature_schema,
        "preprocessing": pipeline,
        "model": model,
        "classes": list(model.classes_)
    }
    
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(artifact, "artifacts/model.joblib")
    logger.info(f"Model artifact saved to artifacts/model.joblib [Version: {artifact['model_version']}]")
