from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import pandas as pd

def build_preprocessing_pipeline() -> Pipeline:
    """
    Builds a Scikit-Learn pipeline for imputation and scaling.
    This guarantees no data leakage as it is fit solely on the training set.
    """
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value=0.0)),
        ('scaler', StandardScaler())
    ])
    return pipeline
