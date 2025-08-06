"""
7) Punctuation (use regex)
    - opening i.e. ( [ 
        parent should be forwards
    - closing i.e. ) ]
        parent should be backwards
    - open/close i.e. ' "
        can have either parent
    - ending i.e. , ; .
        point backwards

steps
get punctuation token along with parent
check under which pnx type it falls
see if the type is consistent with the parent location
if not, return an error dict
"""
# check under which pnx type it falls
from .common_functions import get_sentence_column_data, get_token_details

# TODO: enums looks better here
def get_pnx_type(pnx_token_form: str):
    pnx_types = {
        'ending_pnx': '..,;:?!؟،؛!.', # parent should be backwards
        'opening_pnx': '«([{', # parent should be forwards
        'closing_pnx': '»)]}', # parent should be backwards
        'either_pnx': '—"\'\`' # parent can be either
    }
    for k, v in pnx_types.items():
        if pnx_token_form in v:
            return k
    return 'not_pnx'

def compare_pnx_type_to_parent(pnx_type: str,  pnx_id: int, pnx_parent_token_id: int):
    err_dict = {"flagged_issue": 'FLAG_PNX_POSITION', 'token_id': pnx_id}
    if pnx_type in ['not_pnx', 'either_pnx']: # not pnx or parent can be either, return no error
        return {}
    elif pnx_type in ['ending_pnx', 'closing_pnx']: # parent should be backwards
        if int(pnx_parent_token_id) > pnx_id:
            return err_dict
    elif pnx_type in ['opening_pnx']: # parent should be forwards
        if int(pnx_parent_token_id) < pnx_id:
            return err_dict
    else:
        raise ValueError(f'invalid case in pnx_check! pnx_type: {pnx_type},  pnx_id: {pnx_id}, pnx_parent_token_id: {pnx_parent_token_id}')
    return {}

# get punctuation token along with parent
def flag_pnx_errors(pnx_id, pnx_token_form, pnx_parent_token_id, pnx_parent_form):
    # if the child and parent forms match, they can attach in either direction.
    if pnx_parent_form == pnx_token_form:
        return {}
    
    pnx_type = get_pnx_type(pnx_token_form)
    return compare_pnx_type_to_parent(pnx_type, pnx_id, pnx_parent_token_id)

def pnx_checker(df):
    token_id_col = get_sentence_column_data(df, "ID")
    token_form_col = get_sentence_column_data(df, "FORM")
    token_parent_id_col = get_sentence_column_data(df, "HEAD")
    
    err_list = []
    for tok_id, tok_form, token_parent_id in zip(token_id_col, token_form_col, token_parent_id_col):
        token_parent = get_token_details(df, token_parent_id)
        err_dict = flag_pnx_errors(tok_id, tok_form, token_parent_id, token_parent['FORM'])
        if err_dict:
            err_list.append(err_dict)
    return err_list