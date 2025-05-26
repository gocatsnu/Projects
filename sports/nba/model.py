import pandas as pd

def predict(df: pd.DataFrame) -> pd.Series:
    """Return dummy predictions."""
    return pd.Series(0.0, index=df.index)
