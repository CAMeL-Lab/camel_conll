"""
1) Check if a punctuation mark exists in the middle of the sentence.
If it does, make sure:
    tokens before it do not connect to it or tokens after it
    tokens after it do not connect to it or tokens before it

2) Check if an ending punctuation mark . ? or ! exists within a pair of quotes or brackets
Flag if it does

3) if consecutive punctuation marks attach to each other and are not the same,
Flag



The flag will be on the sentence level

check if the sentence contains a punctuation mark, and that it is not the last token
using the ID of the punctuation mark,
    ensure tokens before the punctuation mark do not connect to it or tokens after it
    ensure tokens after the punctuation mark do not connect to it or tokens before it

tree is flagged if:
    a token attaches to the punctuation mark or before/after the punctuation mark (4 cases)
tree is not flagged if:
    punctuation mark is in the end of the sentence
    punctuation mark is in the middle, and none of the above cases are found
"""

import re
from .common_functions import get_sentence_column_data

def do_tokens_before_connect_after_pnx(tokens_before, pnx_token_id):
    """Checks if tokens before the pnx don't attach after the pnx

    Args:
        tokens_before (DataFrame): tokens before the pnx
        pnx_token_id (int): ID of the pnx

    Returns:
        boolean: whether or not they pass the pnx
    """
    # if all tokens before the given pnx don't attach after (excluding attaching to root)
    return all(int(tok["HEAD"]) < pnx_token_id for tok in tokens_before)

def do_tokens_after_connect_before_pnx(tokens_after, pnx_token_id):
    """Checks if tokens after the pnx don't attach before the pnx

    Args:
        tokens_after (DataFrame): tokens after the pnx
        pnx_token_id (int): ID of the pnx

    Returns:
        boolean: whether or not they pass the pnx
    """
    # if any token after the given pnx attaches before (excluding attaching to root)
    return not any(
        int(tok["HEAD"]) != 0 and int(tok["HEAD"]) <= pnx_token_id
        for tok in tokens_after
    )

def is_same_pnx_or_valid_attachment(current_token, one_token_before, one_token_after):
    # if the forms are the same, then they are similar to two period tokens (. .)
    # if they aren't, then run the same attachment check on the single pnx mark
    # one_token_before and one_token_after can be empty dictionaries if the current_token is at the beginning or end.
    # in this case, the bool value is given true because it is ignored.
    if one_token_before:
        before_bool = current_token["FORM"] == one_token_before["FORM"] or do_tokens_before_connect_after_pnx([one_token_before], current_token["ID"])
    else:
        before_bool = True
    if one_token_after:
        after_bool = current_token["FORM"] == one_token_after["FORM"] or do_tokens_after_connect_before_pnx([one_token_after], current_token["ID"])
    else:
        after_bool = True
    return before_bool and after_bool

def is_valid_token_attachments_to_pnx(df, cur_id):
    # Check if the token exactly before/after the current token is a similar pnx mark.
    # If so, it can attach to the current pnx token
    one_token_before = {} if cur_id == 1 else df[df["ID"] == cur_id-1].to_dict('records')[0]
    one_token_after = {} if cur_id == df.shape[0] else df[df["ID"] == cur_id+1].to_dict('records')[0]
    current_token = df[df["ID"] == cur_id].to_dict('records')[0]
    adjacent_tokens_good = is_same_pnx_or_valid_attachment(current_token, one_token_before, one_token_after)
    
    # check token attachments to and before pnx
    # check token attachments to and after pnx
    tokens_before = df[df["ID"] < cur_id-1].to_dict('records')
    tokens_after = df[df["ID"] > cur_id+1].to_dict('records')
    return adjacent_tokens_good and do_tokens_before_connect_after_pnx(tokens_before, cur_id) and do_tokens_after_connect_before_pnx(tokens_after, cur_id)
    
def is_valid_token_attachments(df, end_pnx_id_list):
    """Check validity of token attachments around punctuation marks in
    end_pnx_id_list (excluding pnx at the end of the df)

    Args:
        df (DataFrame): sentence tokens (excluding last pnx marks)
        end_pnx_id_list (list[int]): indices of sentence pnx marks

    Returns:
        boolean: whether or not all token attachments are valid
    """
    final_bool = True
    for cur_id in end_pnx_id_list:
        final_bool = final_bool and is_valid_token_attachments_to_pnx(df, cur_id)
    
    return final_bool

def drop_last_pnx_marks(df, pnx_id_list):
    """Since we aren't interested in the last pnx mark (or marks in the case of ...),
    they are dropped recursively from the DataFrame before the pnx mark check."""
    if df.empty:
        return df
    elif int(df.tail(1)['ID'].iloc[0]) in pnx_id_list:
        pnx_id_list.remove(int(df.tail(1)['ID'].iloc[0]))
        df.drop(df.tail(1).index, inplace=True) # drop from df
        return drop_last_pnx_marks(df, pnx_id_list)
    return df

def get_mid_pnx_ids(df):
    # pnx_pattern = '|'.join(['\.*', '\?*', '\!*', '\؟*'])
    pnx_pattern = '|'.join(['\.', '\?', '\!', '\؟'])
    
    pnx_id_list = list(df[df["FORM"].str.contains(pnx_pattern)]["ID"])
    df = drop_last_pnx_marks(df, pnx_id_list)
    # return list(df.drop(df.tail(1).index)[df["FORM"].str.contains(pnx_pattern)]["ID"])
    return pnx_id_list

def is_valid_paren_pnx(df):
    # 'ending_pnx': '..,;:?!؟،؛!.'
    # 'opening_pnx': '«([{'
    # 'closing_pnx': '»)]}'
    # 'either_pnx': '—"\'\`
    # reg_pattern = r'([\«\(\[\{\"\']).*[\.\.\,\;\:\?\!\؟\،\؛\!\.].*([\»\)\]\}\'\"])'
    reg_pattern = r'([\«\(\[\{\"\']).*[\.\.\?\!\؟\!\.].*([\»\)\]\}\'\"])'
    # reg = re.compile(reg_pattern)
    sent = ' '.join(get_sentence_column_data(df, 'FORM'))

    # if there is no match, the line below returns true
    return not re.search(reg_pattern, sent)


def mid_pnx_checker(main_df):
    df = main_df.copy()
    # just get the punctuation in the middle of the sentence
    mid_sentence_pnx_id_list = get_mid_pnx_ids(df)
    
    if len(mid_sentence_pnx_id_list) == df.shape[0] or \
        (is_valid_paren_pnx(df) and 
        is_valid_token_attachments(df, mid_sentence_pnx_id_list)):
        return []
    else:
        return [{"flagged_issue": "FLAG_MID_PNX_ATT"}]