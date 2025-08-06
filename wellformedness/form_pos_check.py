"""
TODO: update documentation (TokenInfo type added)
4) Check validity of FORM/UPOS pairs
    - Look up FORM using cameltools. Check if
        - the FORM does not exist
        - the FORM/UPOS pair does not exist

    given words split into multiple tokens,
    combine words with their clitics, as well as POS tags
    place them in a list of tuples
    
    take the original text, tokenize and disambiguate.
    
    the lengths of the above 2 should be the same
    
    iterate through both,
    check if the original combination exists
        if it doesn't, add the error
    check if the form/upos pair exists
        if it doesn't, add the error
    

"""
from dataclasses import dataclass
import re
from typing import List
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.utils.dediac import dediac_ar as camel_dediac
from camel_tools.utils.charsets import AR_CHARSET
from .clitic_check import is_clitic, remove_elided_part
from .common_functions import get_sentence_column_data
from .data_structures import CatibTag
from .prt_token_pos_dict import prt_token_pos_dict

FORM_EXCEPTION_LIST = ['إيا', 'لقد']
IGNORE_ANALYSIS = True

def is_matching_pos(original_pos: str, pos_analysis: str) -> bool:
    """Compares the original token pos to the pos from the MLEDisambiguator analysis.

    Args:
        original_pos (str): original POS tag
        pos_analysis (str): POS tag from the analysis

    Returns:
        bool: returns true if the tags match
    """
    return original_pos == pos_analysis

def is_matching_form(original_form: str, form_analysis: str) -> bool:
    """Compares the original token form to a form from the MLEDisambiguator analysis.

    Args:
        original_form (str): token from the dependency tree
        form_analysis (str): atbtok from the analysis

    Returns:
        bool: returns true if the forms match
    """
    return '+' not in form_analysis and \
        camel_dediac(form_analysis) == camel_dediac(original_form)

@dataclass
class TokenInfo():
    token_id: int
    token: str
    pos_tag: str

def is_valid_clitic_and_pos(token_info: TokenInfo, prt_token_pos_dict: dict) -> dict:
    """Checks if the given clitic and pos tokens are valid.

    Elided tokens are included

    Args:
        token_info (TokenInfo): contains the token, token POS tag, and id in the original list
        prt_token_pos_dict (dict): a dictionary of MSA and dialectal clitics 

    Returns:
        dict: either an out-of-vocab error, or form-pos mismatch error. Empty dict if no error exists
    """
    tok = remove_elided_part(token_info.token)
    
    if tok not in prt_token_pos_dict: # out of vocab, no match    
        return {"flagged_issue": 'FLAG_FORM_OOV', 'token_id': token_info.token_id+1}

    if token_info.pos_tag in prt_token_pos_dict[tok]:
        return {} # valid token & pos, return no error
    else: # only valid pos
        return {"flagged_issue": 'FLAG_FORM_POS_MISMATCH', 'token_id': token_info.token_id+1}

def token_contains_invalid_characters(token):
    # Concatenate all Arabic characters into a string
    ar_str = u''.join(AR_CHARSET)

    # Compile a regular expression using above string
    arabic_re = re.compile(f'^[{re.escape(ar_str)}]+$')

    token = token.replace('(*)', '')
    return not arabic_re.match(token)

def is_float(token):
    try:
        float(token)
        return True
    except ValueError:
        return False

def is_empty_token(token):
    return token == ''

def is_number(token, pos_tag):
    return bool(token.isdigit() or is_float(token)) and pos_tag in [CatibTag.NOM.name, CatibTag.PROP.name]

def is_pnx(pos_tag):
    return pos_tag == CatibTag.PNX.name

def flag_form_pos_errors(token_info: TokenInfo, prt_token_pos_dict: dict, analyzer: Analyzer):
    """Generates errors for invalid clitics and base word tokens.

    Args:
        token_info (TokenInfo): contains the token, token POS tag, and id in the original list
        prt_token_pos_dict (dict): contains the list of particles to check if a clitic token is valid
        analyzer (Analyzer): cameltools analyzer

    Returns:
        dict: either an out-of-vocab error, or form-pos mismatch error. Empty dict if no error exists
    """
    if is_empty_token(token_info.token):
        return {"flagged_issue": 'FLAG_FORM_OOV', 'token_id': token_info.token_id+1}
    
    if is_clitic(token_info.token): # if it starts/ends with a +
        return is_valid_clitic_and_pos(token_info, prt_token_pos_dict)
    
    # replacing - in VRB-PASS to VRB_PASS,
    # checking if pos tag exists in enum
    if token_info.pos_tag == CatibTag.FOREIGN.name:
        return {} # FOREIGN is OOV by default, no issue returned

    # if it's a punctuation mark or a number then possibly no error
    if is_pnx(token_info.pos_tag) or is_number(token_info.token, token_info.pos_tag):
        return {}

    # Non-foreign tokens (handled above) containing
    # non-arabic letters are flagged.
    # (*) are excluded
    # clitics have been handled above, so + was taken care of.
    # Example: و(+) the parens are not valid
    if token_contains_invalid_characters(token_info.token):
        return {"flagged_issue": 'FLAG_FORM_OOV', 'token_id': token_info.token_id+1}
        

    # When set to true, do not perform token analysis
    if IGNORE_ANALYSIS:
        return {}

    analyses = analyzer.analyze(token_info.token)
    # iterate analyzer list of the token
    
    if not analyses: # no analysis found
        return {"flagged_issue": 'FLAG_FORM_OOV', 'token_id': token_info.token_id+1}
    
    form_match = False
    pos_match = False
    for analysis in analyses:
        if is_matching_form(token_info.token, analysis['atbtok']):
            form_match = True
            if is_matching_pos(token_info.pos_tag, analysis['catib6']):
                pos_match = True
                break
    if not form_match and token_info.token not in FORM_EXCEPTION_LIST:
        return {"flagged_issue": 'FLAG_FORM_OOV', 'token_id': token_info.token_id+1}
    elif not pos_match:
        return {"flagged_issue": 'FLAG_FORM_POS_MISMATCH', 'token_id': token_info.token_id+1}
    else: # token and pos match, no error
        return {}


def form_pos_checker(conllx_df, analyzer: Analyzer) -> List[dict]:
    # sourcery skip: for-append-to-extend, use-named-expression
    """Returns a list of errors pertaining to out-of-vocab and from-pos mismatch

    Args:
        conllx_df (DataFrame): a single dependency tree
        analyzer (Analyzer): cameltools analyzer

    Returns:
        List[dict]: list of errors
    """
    token_col = get_sentence_column_data(conllx_df, "FORM")
    pos_col = get_sentence_column_data(conllx_df, "UPOS")
    token_pos_pairs = [TokenInfo(idx, tok, pos) for idx, (tok, pos) in enumerate(zip(token_col, pos_col))]

    err_list = []
    for token_info in token_pos_pairs:
        token_err = flag_form_pos_errors(token_info, prt_token_pos_dict, analyzer) 
        if token_err: # error is not an empty dict; it exists
            err_list.append(token_err)
    return err_list
