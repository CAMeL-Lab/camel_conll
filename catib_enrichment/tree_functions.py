from dataclasses import asdict, dataclass
import re
from typing import Union

from pandas.core.frame import DataFrame

from camel_tools.utils.charmap import CharMapper
ar2bw = CharMapper.builtin_mapper('ar2bw')
bw2ar = CharMapper.builtin_mapper('bw2ar')

# not using:
# token_id: int
# form: str
# head: int
# parent_id: int
# parent_form: str

@dataclass
class SentenceToken:
    token_id: int
    lex: str
    catib_pos: str
    mada_pos: str
    
    parent_id: int
    parent_lex: str
    parent_catib_pos: str
    parent_mada_pos: str
    
    rel: str
    order: str

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items() if k not in ['token_id', 'parent_id']}

def get_mada(feats, misc):
    # ud=NOUN|pos=noun|prc3=0|prc2=0|prc1=0|prc0=Al
    try:
        mada_feat = feats.split('|')[1]
        if not mada_feat.startswith('pos'): # mada pos could be in the MISC column
            pattern = r"mada=([a-z]+\_?[a-z]+)"
            mada_feat = f"pos={re.search(pattern, misc)[1]}"
    except:
        mada_feat = 'pos=*'
    assert mada_feat.startswith('pos'), f'mada feat: {mada_feat}, it should start with pos'
    return mada_feat.split('=')[1]

def get_parent_id(sen_df: DataFrame, current_token_id: int) -> int:
    """gets the id of the parent of the curent token

    Args:
        current_token_id (int): token id
        conllx_df (DataFrame): dependency tree

    Returns:
        int: parent id
    """
    if current_token_id == 0: # root has no parent
        return -1
    return int(sen_df[sen_df['ID'] == current_token_id].to_dict('records')[0]['HEAD'])

def get_token_details(sen_df, tok_id) -> Union[SentenceToken, dict]:
    """Returns a dictionary of token details, in ConllX format"""
    if type(tok_id) == int:
        pass
    elif tok_id.isdigit():
        tok_id = int(tok_id)
    else:
        raise ValueError("invalid parent ID!")
    temp_details = sen_df[sen_df["ID"] == tok_id].to_dict('records')
    
    if temp_details:
        temp_details = temp_details[0]
        new_lex = '*' if temp_details['LEMMA'] == '_' else ar2bw(temp_details['LEMMA'])

        return SentenceToken(
            token_id=temp_details['ID'],
            lex=new_lex,
            catib_pos=temp_details['UPOS'],
            mada_pos=get_mada(temp_details['FEATS'], temp_details['MISC']),
            parent_lex="",
            parent_id=-1,
            parent_catib_pos="",
            parent_mada_pos="",
            rel=temp_details['DEPREL'],
            order=""
        )
    elif tok_id == 0:
        return SentenceToken(
            token_id=0,
            lex="ROOT",
            catib_pos="ROOT",
            mada_pos="ROOT",
            parent_id=-1,
            parent_lex="",
            parent_catib_pos="",
            parent_mada_pos="",
            rel="---",
            order="",
        )
    else:
        return {}

def add_parent_details(sen_df, child: SentenceToken):
    # checks if parent exists and assigns it to parent_df_dict_item
    parent_id = get_parent_id(sen_df, child.token_id)
    
    if parent_df_dict_item := get_token_details(sen_df, parent_id):
        # setattr(child, parent_id, parent_df_dict_item.token_id)
        child.parent_id = parent_df_dict_item.token_id
        child.parent_lex = ar2bw(parent_df_dict_item.lex)
        child.parent_catib_pos = parent_df_dict_item.catib_pos
        child.parent_mada_pos = parent_df_dict_item.mada_pos
    else:
        raise ValueError('parent not found')

def add_order(child: SentenceToken):
    child.order = 'P-C' if child.parent_id < child.token_id else 'C-P'
