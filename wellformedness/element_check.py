"""
#!: FOREIGN added
1) Element values
    - the IDs are consecutive, nonnegative integers, starting from 1
    - the UPOS tags are valid CATiB tags
    - the XPOS tags (if used) are valid CATiBex tags
    - the DEPREL tags are valid relation labels
"""

from typing import List

from pandas.core.frame import DataFrame

from .common_functions import get_sentence_column_data

TAG_SET = {
    'CATIB_TAGS': ['NOM', 'PROP', 'VRB', 'VRB-PASS', 'PRT', 'PNX', 'FOREIGN'],
    'DEPREL_LABELS': ['SBJ', 'OBJ', 'TPC', 'PRD', 'IDF', 'TMZ', 'MOD', '---'],
    'CATIBEX_TAGS': ['Al-NOM', 'Al-NOM-A', 'Al-NOM-An', 'Al-NOM-At', 'Al-NOM-p', 
                    'Al-NOM-w', 'Al-NOM-wn', 'Al-NOM-y', 'Al-NOM-yn', 'NOM', 
                    'NOM-A', 'NOM-An', 'NOM-At', 'NOM-PREP', 'NOM-PRON', 'NOM-PROP', 
                    'NOM-p', 'NOM-w', 'NOM-wn', 'NOM-y', 'NOM-yn', 'NUM-NOM', 'PNX', 
                    'PNX-COMMA', 'PNX-DASH', 'PNX-DOT', 'PNX-PRN', 'PNX-QUOTE', 'PRT', 
                    'PRT-An', 'PRT-NEG', 'PRT-PREP', 'PRT-V', 'PRT-b', 'PRT-f', 
                    'PRT-l', 'PRT-mA', 'PRT-w', 'VRB', 'VRB-PASS', 'VRB-PASS-s', 'VRB-s',
                    'FOREIGN']
    }
# check the link for tags:
# cat ~/.camel_tools/data/morphology_db/calima-msa-r13/calima-msa-s31_0.4.2.utf8.db |grep -v "lex" |grep "\t.*Suff.*\t"|grep catib6:NOM|wc
#      833   20677  301694
# lab tactics


def check_tags(col_tag_list: List[str], tag_set: str) -> List[int]:
    """Given a sentence column list, determine whether or not its tokens contain
    valid tags.
    
    example: check for valid CATiB tags:
    tag_list will contain the UPOS column of a sentence
    tag_set will contain the tag_set to compare to (CATIB_TAGS in this case)

    NOTE: id is incremented before being added to the return list because
        ConllX format starts from 1, not 0

    Args:
        col_tag_list (List[str]): a single sentence column
        tag_set (str): tag set used to check validity of column items

    Returns:
        List[int]: id list; token locations with invalid tags.
    """
    return [
        {'token_id': id + 1, "flagged_issue": f"FLAG_{tag_set}"}
        for id, col_tag in enumerate(col_tag_list)
        if col_tag not in TAG_SET[tag_set]
    ]

def element_checker(sen_df: DataFrame) -> dict:
    """Given a dependency tree DataFrame, return a dictionary
    containing ID, CATiB, and dependency relation errors.

    Args:
        sen_df (DataFrame): a dependency tree

    Returns:
        dict: a dictionary or four element-level errors
    """
    token_col = get_sentence_column_data(sen_df, "FORM")
    id_col = get_sentence_column_data(sen_df, "ID")

    # id_err = check_ids(id_col)
    catib_err = check_tags(get_sentence_column_data(sen_df, "UPOS"), 'CATIB_TAGS')
    # catibex_err = check_tags(get_sentence_column_data(sen_df, "XPOS"), token_col, 'CATIBEX_TAGS')
    deprel_err = check_tags(get_sentence_column_data(sen_df, "DEPREL"), 'DEPREL_LABELS')
    # return id_err + catib_err + catibex_err + deprel_err
    return catib_err + deprel_err
