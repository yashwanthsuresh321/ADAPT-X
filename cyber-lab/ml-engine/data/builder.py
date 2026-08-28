import pandas as pd
import logging
from typing import Tuple

logger = logging.getLogger("data.builder")

def build_labeled_dataset(features_df: pd.DataFrame, scenarios_df: pd.DataFrame) -> pd.DataFrame:
    """
    Joins behavioral_features with ml_scenarios based on overlapping time windows.
    Returns a dataframe with ground-truth labels.
    """
    if features_df.empty or scenarios_df.empty:
        logger.warning("Empty features or scenarios dataframe. Cannot build dataset.")
        return pd.DataFrame()
        
    # Ensure datetime types
    features_df['window_start'] = pd.to_datetime(features_df['window_start'], utc=True)
    features_df['window_end'] = pd.to_datetime(features_df['window_end'], utc=True)
    scenarios_df['window_start'] = pd.to_datetime(scenarios_df['window_start'], utc=True)
    scenarios_df['window_end'] = pd.to_datetime(scenarios_df['window_end'], utc=True)
    
    labeled_records = []
    
    for _, feature_row in features_df.iterrows():
        f_start = feature_row['window_start']
        f_end = feature_row['window_end']
        
        # Find matching scenarios where the feature window overlaps or is contained
        # We consider an overlap if feature window starts before scenario ends and ends after scenario starts.
        # But to be safer (preventing ambiguity), we demand the feature window starts and ends roughly within the scenario.
        
        matches = scenarios_df[
            (scenarios_df['window_start'] <= f_start) & 
            (scenarios_df['window_end'] >= f_end)
        ]
        
        if len(matches) == 1:
            label = matches.iloc[0]['label']
            record = feature_row.to_dict()
            record['label'] = label
            labeled_records.append(record)
        elif len(matches) > 1:
            logger.warning(f"Ambiguous overlapping scenarios for feature {feature_row['feature_id']}. Dropping.")
        else:
            # No scenario matched. It is unlabelled data (could be ambient noise). We drop it from training.
            pass
            
    dataset = pd.DataFrame(labeled_records)
    logger.info(f"Built labeled dataset with {len(dataset)} samples.")
    return dataset

def prepare_feature_vectors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flattens the feature_vector JSONB/dict into separate columns dynamically.
    Ensures deterministic ordering.
    """
    if df.empty:
        return df
        
    # Extract the dictionary elements into separate columns
    # Pandas json_normalize handles this well
    vectors_df = pd.json_normalize(df['feature_vector'])
    
    # Sort columns alphabetically to ensure deterministic schema
    vectors_df = vectors_df.reindex(sorted(vectors_df.columns), axis=1)
    
    # Concat labels and other necessary non-feature columns
    # We only keep 'feature_id', 'window_start' (for temporal splits) and 'label' alongside features.
    
    # Drop any conflicting columns from vectors_df
    for col in ['window_start', 'window_end', 'feature_id', 'label']:
        if col in vectors_df.columns:
            vectors_df = vectors_df.drop(columns=[col])
            
    meta_df = df[['feature_id', 'window_start', 'label']].reset_index(drop=True)
    
    final_df = pd.concat([meta_df, vectors_df], axis=1)
    return final_df
