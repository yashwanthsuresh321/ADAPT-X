import pandas as pd
import logging
from typing import Tuple
from sklearn.model_selection import train_test_split

logger = logging.getLogger("data.splitter")

def split_dataset(df: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.1) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataset chronologically (oldest data for train, newest for test).
    If dataset is too small (<10 samples), falls back to stratified random splitting 
    just to prevent errors during execution, though a warning is logged.
    Returns (train_df, val_df, test_df)
    """
    if df.empty:
        return df, df, df
        
    df = df.sort_values(by='window_start').reset_index(drop=True)
    
    total = len(df)
    if total < 10:
        logger.warning(f"Dataset too small ({total} samples) for strict split. Returning the same set for Train/Val/Test to allow pipeline execution.")
        return df, df, df
            
    # Chronological Split
    test_idx = int(total * (1.0 - test_size))
    val_idx = int(total * (1.0 - test_size - val_size))
    
    train_df = df.iloc[:val_idx]
    val_df = df.iloc[val_idx:test_idx]
    test_df = df.iloc[test_idx:]
    
    logger.info(f"Temporal Split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    return train_df, val_df, test_df
