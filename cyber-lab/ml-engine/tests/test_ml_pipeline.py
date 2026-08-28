import pytest
import pandas as pd
from data.builder import build_labeled_dataset, prepare_feature_vectors
from data.splitter import split_dataset
from features.selector import select_features
from features.transformer import build_preprocessing_pipeline
from models.baseline import get_baseline_model

def test_builder_logic():
    features = pd.DataFrame([
        {"feature_id": "1", "window_start": "2026-08-28T10:05:00Z", "window_end": "2026-08-28T10:06:00Z", "event_count": 5}
    ])
    scenarios = pd.DataFrame([
        {"scenario_id": "S1", "label": "benign", "window_start": "2026-08-28T10:00:00Z", "window_end": "2026-08-28T10:30:00Z"}
    ])
    dataset = build_labeled_dataset(features, scenarios)
    assert len(dataset) == 1
    assert dataset.iloc[0]["label"] == "benign"

def test_feature_preparation():
    df = pd.DataFrame([
        {"feature_id": "1", "window_start": "2026-08-28T10:05:00Z", "label": "benign", "feature_vector": {"event_count": 5, "unique_services": 2}}
    ])
    flat = prepare_feature_vectors(df)
    assert "event_count" in flat.columns
    assert "unique_services" in flat.columns
    assert "label" in flat.columns

def test_feature_selection():
    df = pd.DataFrame([
        {"feature_id": "1", "window_start": "2026-08-28T10:05:00Z", "label": "benign", "event_count": 5, "unique_services": 2}
    ])
    sel = select_features(df)
    assert "feature_id" not in sel.columns
    assert "label" not in sel.columns
    assert "event_count" in sel.columns
    assert len(sel.columns) == 2

def test_pipeline_no_leakage():
    df = pd.DataFrame([
        {"event_count": 5},
        {"event_count": None},
        {"event_count": 15}
    ])
    pipeline = build_preprocessing_pipeline()
    transformed = pipeline.fit_transform(df)
    assert round(transformed[1][0], 2) == -1.07  # the mean of (5,0,15) scaled
