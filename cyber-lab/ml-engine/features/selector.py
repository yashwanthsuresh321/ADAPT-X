import pandas as pd
from typing import List

def select_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects numerical behavioral features only, explicitly discarding IDs or string arrays.
    """
    # Columns to drop because they are identifiers or target labels
    drop_cols = ['feature_id', 'window_start', 'label', 'behavior_sequence']
    
    # Actually, behavior_sequence is a list, let's just keep numeric cols.
    # The JSON flatten in prepare_feature_vectors already extracted numericals.
    # We will explicitly drop metadata and non-numeric columns.
    
    df_features = df.copy()
    for col in drop_cols:
        if col in df_features.columns:
            df_features = df_features.drop(columns=[col])
            
    # Also drop anything that is clearly not numeric/boolean
    numeric_df = df_features.select_dtypes(include=['number', 'bool'])
    
    return numeric_df
