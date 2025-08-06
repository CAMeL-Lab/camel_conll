"""Conllx checks will be added here

Checks if IDs are consecutive
"""
from .common_functions import get_sentence_column_data

def is_valid_id_list(conllx_df):
    """Checks if the ID column contains conscutive numbers

    Args:
        conllx_df (DataFrame): sentence DataFrame
    """
    expected_ids = list(range(1, conllx_df.shape[0]+1))
    id_col = get_sentence_column_data(conllx_df, 'ID')
    
    return expected_ids == id_col

def is_valid_head_list(conllx_df):
    """Checks if the parent IDs exist as token IDs

    Args:
        conllx_df (DataFrame): sentence DataFrame
    """
    # 0 added for when parent is root
    id_col = get_sentence_column_data(conllx_df, 'ID') + [0]
    head_col = get_sentence_column_data(conllx_df, 'HEAD')
    return all(head in id_col for head in head_col)

def conllx_checker(conllx_df):
    length = conllx_df.shape[0]
    
    if is_valid_head_list(conllx_df) and is_valid_id_list(conllx_df):
        return []
    else:
        return [{"flagged_issue": "FLAG_ID_OR_HEAD"}]
