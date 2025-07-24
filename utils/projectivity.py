"""
5) Projectivity
    - Projectivity list
        Check if the projection returns a list of consecutive integers (IDs)
    - Cycle check
        nodes should not be visited twice
    - Disconnected node/cycle
        Missing numbers from projectivity list
    - Child should not point to itself
    - Every token has to be a child of something (see last point of root)
"""
from typing import List
from pandas import DataFrame

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

def update_ordered_tokens(
    parent_token_id: int,
    children_ids: List[int], 
    ordered_tokens: List[int]
    ) -> List[int]:
    """Update ordered_tokens list by first combining the parent and children
    ids, sorting them, then replacing the parent in ordered_tokens with the 
    result.

    Args:
        parent_token_id (int): parent id
        children_ids (List[int]): children ids
        ordered_tokens (List[int]): list of ids to determine projectivity

    Returns:
        List[int]: new ordered_tokens list
    """
    parent_and_children_ids = children_ids.copy()
    parent_and_children_ids.append(parent_token_id)
    temp_list = sorted(parent_and_children_ids)
    p_tok_location = ordered_tokens.index(parent_token_id)
    return ordered_tokens[:p_tok_location] + temp_list + ordered_tokens[p_tok_location+1:]

def get_projectivity_list(current_token_id: int, conllx_df: DataFrame, ordered_tokens: List[int] = None) -> List[int]:
    """projectivity algorithm
    let ordered_tokens be the final list to check for projectivity
    let root be p_tok (for parent token)
    let children of p_tok be c_tok_list
    if c_tok_list is empty
        return the list of ordered_tokens
    else
        get order of p_tok and c_tok_list and update ordered_tokens
        run alg on each child, passing ordered_tokens
        the return value is ordered_tokens

    Args:
        current_token_id (int): parent id
        conllx_df (DataFrame): dependency tree DataFrame
        ordered_tokens (List[int], optional): list of tokens in projective order. Defaults to [0].

    Returns:
        List[int]: [description]
    """
    if ordered_tokens is None:
        ordered_tokens = [0]
    children = get_children_ids_of(current_token_id, conllx_df)
    if not children:
        return ordered_tokens
    ordered_tokens = update_ordered_tokens(current_token_id, children, ordered_tokens)
    for child in children:
        ordered_tokens = get_projectivity_list(child, conllx_df, ordered_tokens)
    return ordered_tokens
    

def projective_checker(conllx_df: DataFrame) -> dict:
    """Given a tree DataFrame, determine whether or not it is projective.

    Args:
        conllx_df (DataFrame): a dependency tree DataFrame

    Returns:
        dict: key is PROJECTIVITY, value is true or false
    """
    proj_list = get_projectivity_list(0, conllx_df)
    # return {'PROJECTIVITY': list(range(len(proj_list))) == proj_list}
    if proj_list != list(range(len(proj_list))):
        return [{"flagged_issue": "FLAG_NONPROJECTIVE"}]
    else:
        return []
    # return list(range(len(proj_list))) == proj_list
