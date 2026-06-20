"""
src/utils/validators.py
=======================
General utility validators for the pipeline.
"""

import pandas as pd

def validate_dataframe(df: pd.DataFrame, name: str = "dataframe") -> None:
    """Check if the provided object is a pandas DataFrame.
    
    Parameters
    ----------
    df : any
        The object to validate.
    name : str, optional
        The name to use in the error message, by default "dataframe".
        
    Raises
    ------
    TypeError
        If `df` is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a pandas DataFrame for '{name}', but got {type(df).__name__}.")
