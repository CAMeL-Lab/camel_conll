from typing import List, Set
from pandas import DataFrame

def update_column_order(df: DataFrame, all_columns: List[str]) -> DataFrame:
    current_columns = set(df.columns)
    new_columns = [col for col in all_columns if col in current_columns]
    return df[new_columns]

def set_numeric_columns_to_int(df: DataFrame, string_columns: Set[str]) -> DataFrame:
    """Sets numeric columns to int. Float columns are also converted to remove the decimal from counts.

    Args:
        df (DataFrame): contains stats of a file
        string_columns (Set[str]): columns that are not numeric (currently only the file name)

    Returns:
        DataFrame: stats with adjusted datatypes
    """
    # Change NaN to 0.0.
    # get numeric columns and cast to int.
    cols = list(set(df.columns) - string_columns)
    df[cols] = df[cols].fillna(0.0).astype(int)
    
    return df