"""
3) Pro/enclitics
    - an enclitic cannot appear without a base word
        an enclitic cannot come after a proclitic
        an enclitic cannot be the first token
    - a proclitic cannot be the last token
"""

from .common_functions import get_sentence_column_data
import re

def get_plus_toks_regex():
    return re.compile(r'^\++$')

def remove_elided_part(tok):
    """ given a token that ends with (*), remove it.
    """
    return tok[:-3] if tok.endswith('(*)') else tok

def is_clitic(tok, plus_toks=get_plus_toks_regex()):
    """Checks to see if a + exists in the given token,
    but the token is not one or more +'s (i.e. +, +++)
    
    Elided clitics are included.

    Args:
        tok (str): token
        plus_toks (regex): compiled regex to match against

    Returns:
        bool: whether or not it's a clitic
    """
    tok = remove_elided_part(tok)
    return (is_enclitic(tok) or is_proclitic(tok)) and not plus_toks.match(tok)

def is_enclitic(tok):
    return tok.startswith('+')

def is_proclitic(tok):
    return tok.endswith('+')

def is_prev_baseword(current_idx, token_col):
    """
    cases
    enclitic is at the beginning - False
    enclitic proceeds a baseword - True
    enclitic proceeds another enclitic - True
    enclitic proceeds a proclitic - False
    enclitic proceeds a non-char string (pnx)?
    """
    if current_idx == 0: # first token, so no baseword
        return False
    elif is_enclitic(token_col[current_idx-1]):
        return True
    elif is_proclitic(token_col[current_idx-1]): # cannot be preceded by a proclitic
        return False
    return True

def is_next_baseword(current_idx, token_col):
    """
    cases
    proclitic is at the end - False
    proclitic preceded baseword - True
    proclitic preceded proclitic - True
    proclitic preceded enclitic - False
    proclitic preceded nothing - False
    
    """
    if current_idx == len(token_col) - 1: # last token, so no baseword
        return False
    elif is_enclitic(token_col[current_idx+1]): # cannot be followed by an enclitic
        return False
    elif is_proclitic(token_col[current_idx+1]): # can be followed by a proclitic
        return True
    return True


def enclitic_check(token_col, plus_toks):
    return [
        {
            'token_id': idx + 1,
            "flagged_issue": "FLAG_ENCLITIC",
        }
        for idx, tok in enumerate(token_col)
        if is_clitic(tok, plus_toks)
        and is_enclitic(tok)
        and not is_prev_baseword(idx, token_col)
    ]        

def proclitic_check(token_col, plus_toks):
    return [
        {
            'token_id': idx + 1,
            "flagged_issue": "FLAG_PROCLITIC",
        }
        for idx, tok in enumerate(token_col)
        if is_clitic(tok, plus_toks)
        and is_proclitic(tok)
        and not is_next_baseword(idx, token_col)
    ]  

def clitic_checker(df):
    # if a token with one or more +s exists i.e. +++, don't include as a clitic.
    plus_toks = get_plus_toks_regex()
    
    token_col = get_sentence_column_data(df, "FORM")
    
    enc_err_list = enclitic_check(token_col, plus_toks)
    pro_err_list = proclitic_check(token_col, plus_toks)
    return enc_err_list + pro_err_list