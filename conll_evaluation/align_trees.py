
from typing import Tuple
from pandas import DataFrame, concat
from external_libraries.ced_word_alignment.alignment import align_words


def get_new_row() -> DataFrame:
    """Row to be inserted into the DataFrame for alignment.

    Returns:
        DataFrame: the row
    """
    return DataFrame({
        'ID': -1, 'FORM': 'tok', 'LEMMA': '_', 
        'UPOS': '_', 'XPOS': '_', 'FEATS': '_',
        'HEAD': -1, 'DEPREL': '_', 'DEPS': '_', 'MISC': '_'
    }, index=[0])

def insert_empty_row(i: int, df: DataFrame) -> DataFrame:
    """Inserts an empty row into the DataFrame, and adjust the ID and HEAD
    numbering for numbers greater than i+1 (the ID of the inserted row).

    Args:
        i (int): the index of the row to insert, NOT the ID
        df (DataFrame): the DataFrame accepting a row

    Returns:
        DataFrame: the DataFrame with an inserted row and updated IDs and HEADs
    """
    df = concat([df.iloc[:i], get_new_row(), df.iloc[i:]])
    
    # reset index and ID after inserting new row
    df.reset_index(inplace=True, drop=True)
    new_id_column = range(1, df.shape[0]+1)
    df['ID'] = new_id_column
    
    # increment HEADs > inserted row (i+1 because i is the row index and not ID)
    tok_ids = df[df['HEAD'] >= i+1].index
    df.loc[tok_ids, 'HEAD'] += 1

    return df

def align_trees(df_1: DataFrame, df_2: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """Aligns words in a sentence, then adds rows to the DataFrames
    if alignment is needed.

    Args:
        df_1 (DataFrame): first tree to align
        df_2 (DataFrame): second tree to align

    Returns:
        tuple(DataFrame, DataFrame): the aligned dataframes
    """
    sentence_1 = (' '.join(list(df_1['FORM']))).replace('+', '')
    sentence_2 = (' '.join(list(df_2['FORM']))).replace('+', '')

    result = align_words(sentence_1, sentence_2)
    for i, word_comp in enumerate(result):
        if word_comp[0] is None:
            df_1 = insert_empty_row(i, df_1)
        if word_comp[1] is None:
            df_2 = insert_empty_row(i, df_2)
    return df_1.reset_index(drop=True), df_2.reset_index(drop=True)
