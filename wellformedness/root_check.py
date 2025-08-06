"""
2) ROOT (HEAD = 0) constraints
    - There exists exactly one root
    - The root has at least one child
        corollary: at least one child has the root as its parent
    - A path can be drawn from the root to every token in the tree
"""
from typing import List
from pandas import DataFrame

from .common_functions import get_token_details

def root_exists(df: DataFrame) -> bool:
    """Given a tree, check if at least one token contains root as a parent.
    In other words, at least one token should have its HEAD == '0'.

    Args:
        df (DataFrame): the dependency tree

    Returns:
        bool: root exists
    """
    return len(df[df["HEAD"] == 0].to_records('dict')) > 0 # and len(list(df[df["DEPREL"] == '---'])) > 0


def is_connected(df: DataFrame, cur_node: dict, visited: List[int], to_root: List[int]) -> bool:
    if cur_node["HEAD"] == 0 or int(cur_node["HEAD"]) in to_root:
        visited.append(cur_node["ID"])
        return to_root + visited
    elif cur_node["ID"] in visited:
        return False
    else:
        visited.append(cur_node["ID"])
        return is_connected(df, get_token_details(df, cur_node["HEAD"]), visited, to_root)

def all_connected_to_root(df: DataFrame) -> bool:
    """For each token, the token should either
        - point to the root
        - point to a token that recursively points to the root
    
    Args:
        df (DataFrame): dependency tree DataFrame
    """
    to_root = []
    for _, row in df.iterrows():
        to_root = is_connected(df, row.to_dict(), [], to_root)
        if not to_root:
            return False
    return True
    # return all(is_connected(df, row.to_dict(), [], []) for _, row in df.iterrows())

def root_checker(df) -> List[dict]:
    # check if a root exists
    # check if tokens recursively reach the root
    if root_exists(df) and all_connected_to_root(df):
        return []
    else:
        return [{"flagged_issue": "FLAG_ROOT_ATT"}]