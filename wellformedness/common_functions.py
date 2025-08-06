from typing import List

from pandas.core.frame import DataFrame
from pandas.core.series import Series

def get_token_details(sen_df, tok_id) -> dict:
    """Returns a dictionary of token details, in ConllX format"""
    if type(tok_id) == int:
        pass
    elif tok_id.isdigit():
        tok_id = int(tok_id)
    else:
        raise ValueError("invalid parent ID!")
    temp_details = sen_df[sen_df["ID"] == tok_id].to_dict('records')
    if temp_details:
        return temp_details[0]
    elif tok_id == 0:
        # return {"ID": 0, "FORM": "ROOT", "UPOS": "___"}
        return {"ID": 0, "FORM": "ROOT", "UPOS": "ROOT", "HEAD": -1, "DEPREL": "---"}
    else:
        return {}

def get_sentence_column_data(sen_df: DataFrame, column_name: str) -> List[Series]:
    """Given a sentence DataFrame, return the data of a column in a list

    Args:
        sen_df (DataFrame): a sentence
        column_name (str): name of column

    Returns:
        list: a column of the DataFrame
    """
    return list(sen_df[column_name])


def get_children_ids_of(current_token_id, conllx_df) -> List[int]:
    """Returns a list of ids of the children of the current token.

    Args:
        current_token_id (int): ID of the parent token
        conllx_df (DataFrame): tree data

    Returns:
        List[int]: list of children ids
    """
    # return list(conllx_df[conllx_df['HEAD'] == str(current_token_id)]["ID"])
    return list(conllx_df[conllx_df['HEAD'] == current_token_id]["ID"])

def add_text_details(item: dict, text: str, text_id: int) -> dict:
    """add text and text id to an invalid token dict

    Args:
        item (dict): erroneous token
        text (str): text of a dependency tree
        text_id (int): dependency tree number

    Returns:
        dict: erroneous token with added text and text_id items
    """
    item['text'] = text
    item['sentence_number'] = text_id
    return item

def add_token_details(item, df_dict_item):
    assert df_dict_item, f'Missing token details! Check if the IDs of sentence number {item.sentence_number} are valid.'
    item['form'] = df_dict_item['FORM']
    if 'pos_tag' not in item:
        item['pos_tag'] = df_dict_item['UPOS']
    item['label'] = df_dict_item['DEPREL']
    
    
def add_parent_details(item, df, token_id):
    # checks if parent exists and assigns it to parent_df_dict_item
    if parent_df_dict_item := get_token_details(df, token_id):
        item['parent_id'] = parent_df_dict_item["ID"]
        item['parent_form'] = parent_df_dict_item["FORM"]
        if 'parent_pos_tag' not in item:
            item['parent_pos_tag'] = parent_df_dict_item["UPOS"]
    else:
        raise ValueError('parent not found')

def add_token_level_details(conllx_df, dict_list) -> List[dict]:
    """add details to list of invalid tokens

    Args:
        conllx_df (DataFrame): sentence object of a dependency tree
        dict_list (List[dict]): erroneous tokens

    Returns:
        List[dict]: erroneous tokens with added details
    """
    # for every erroneous token
    for item in dict_list:
        df_dict_item = get_token_details(conllx_df, item["token_id"])
        try:
            add_token_details(item, df_dict_item)
        except:
            import pdb; pdb.set_trace()
        add_parent_details(item, conllx_df, df_dict_item["HEAD"])
        # add direction
        item['direction'] = 'P-C' if item['parent_id'] < df_dict_item['ID'] else 'C-P'
    return dict_list
