"""A conllx file contains commas that are connected to the next token.
This script connects the comma to the correct token before it.

Usage:
    text_to_conll_cli ((-c <input> | --conll=<input>) | (-d <input> | --dir=<input>) | (-p <input> | --parent_dir=<input>))
        (-o <output> | --output=<output>)
    text_to_conll_cli (-h | --help)

Options:
    -c <input> --conll=<input>
        A CoNLL file
    -d <input> --dir=<input>
        A directory of CoNLL files
    -p <input> --parent_dir=<input>
        A directory of directories of CoNLL files
    -o <output> --output=<output>
        The directory to fixed CoNLL files
    -h --help
        Show this screen.
"""
import pathlib
from typing import List, Union
from pandas import concat, DataFrame
from docopt import docopt

from utils.dir_utils import get_conll_files, remove_file_name_extension
from utils.projectivity import projective_checker
from utils.prt_token_pos import get_prt_token_pos_dict
from conllx_df.conllx_df import ConllxDf

arguments = docopt(__doc__)

# from wellformedness.projectivity_check import projective_checker

# from lib.class_conllx import Conllx


################################################################
### Fix comma functions
################################################################
def is_possible_parent_behind(token_id: int, conllx_df: DataFrame) -> bool:
    # checks if the comma is connected to the token ahead of it
    token_dict = conllx_df[conllx_df['ID'] == token_id].to_dict('records')[0]
    return token_dict['ID'] < int(token_dict['HEAD'])

def can_move_token(token_id, new_parent_id, conllx_df: DataFrame) -> bool:
    # sourcery skip: return-identity
    # performs the following checks:
    # is the the token a root?
    if new_parent_id == 0:
        return False
    # is the the token ahead of the comma?
    if new_parent_id > token_id:
        return False
    # does connecting to the token cause non-projectivity?
    temp_df = conllx_df.copy()
    temp_df = update_comma_head(token_id, new_parent_id, temp_df)
    if projective_checker(temp_df):
        return False
    
    return True

def get_parent_id(current_token_id: int, conllx_df: DataFrame) -> int:
    """gets the id of the parent of the curent token

    Args:
        current_token_id (int): token id
        conllx_df (DataFrame): dependency tree

    Returns:
        int: parent id
    """
    if current_token_id == 0: # the comma is the first token, so parent is an invalid ID of 0
        # import pdb; pdb.set_trace()
        # keep the comma pointing to current token
        return int(conllx_df[conllx_df['ID'] == 1].to_dict('records')[0]['HEAD'])

    return int(conllx_df[conllx_df['ID'] == current_token_id].to_dict('records')[0]['HEAD'])

def update_comma_head(comma_id: int, new_parent_id: int, conllx_df: DataFrame) -> DataFrame:
    """attaches the comma to the new parent

    Args:
        comma_id (int): token id
        new_parent_id (int): the id of the new parent of the comma token
        conllx_df (DataFrame): dependency tree

    Returns:
        DataFrame: updated dependency tree
    """

    conllx_df.iloc[comma_id-1, conllx_df.columns.get_loc('HEAD')] = new_parent_id
    return conllx_df

def get_comma_id_list(conllx_df: DataFrame) -> List[int]:
    """Gets all commas in the sentence

    Args:
        conllx_df (DataFrame): dependency tree DataFrame

    Returns:
        List[int]: list of comma token ids
    """
    comma_tokens = conllx_df[(conllx_df['FORM'] == ',') | (conllx_df['FORM'] == '،')]
    return list(comma_tokens['ID'])

# def fix_comma(comma_id: int, conllx_df: DataFrame) -> Union[DataFrame, Exception]:
def fix_comma(comma_id: int, conllx_df: DataFrame) -> Union[DataFrame, bool]:
    """The algorithm is as follows:
    check if the tree is projective, otherwise raise an exception
    get the token before it
        is the the token a root?
        is the the token ahead of the comma?
        does connecting to the token cause non-projectivity?
    if it is false for all three, connect to the token.
    """
    # tree is not projective (an error list is returned), 
    # so return conllx_df without fixing commas
    if projective_checker(conllx_df):
        # return conllx_df
        raise Exception('tree is not projective')
    # initial new parent is the token before the comma token
    new_parent_id = comma_id - 1

    # the default will be the previous token.
    # if the comma is the first token in the sentence, don't change the parent.
    while True:
        # test the parent of the previous token
        possible_parent_id = get_parent_id(new_parent_id, conllx_df)
        if not can_move_token(comma_id, possible_parent_id, conllx_df):
            break # we can no longer move the token
        else:
            # if we can move the token, update the new parent id
            new_parent_id = possible_parent_id
    
    # conllx_df = update_comma_head(comma_id, new_parent_id, conllx_df)
    return update_comma_head(comma_id, new_parent_id, conllx_df)

def fix_commas(tree_df):
    comma_list = get_comma_id_list(tree_df)
    for comma_id in comma_list:
        try:
            data = fix_comma(comma_id, tree_df)
        except:
            return tree_df
    return data

################################################################
### End of fix comma functions
################################################################

def fix_sentence_commas(tree_df):
    # for sentence in sen_list:
    # import pdb; pdb.set_trace()
    try:
        data = fix_commas(tree_df)
    except:
        return tree_df
    return data

def fix_tags_and_labels(df):
    """Obtain the regex version of particles and pronouns,
    and use them to replace the POS tags of particle and pronoun tokens.

    Args:
        df (DataFrame): sentence dependency tree
    """
    for i, row in df.iterrows():
        if row['FORM'] in get_prt_token_pos_dict() and \
            row['UPOS'] not in get_prt_token_pos_dict()[row['FORM']]:
                # import pdb; pdb.set_trace()
                df.loc[i, 'UPOS'] = get_prt_token_pos_dict()[row['FORM']][0]
    # expr = get_regex_expression_by_tag('PRT')
    # df.loc[df.FORM.str.match(expr), 'UPOS'] = 'PRT'
    # expr = get_regex_expression_by_tag('NOM')
    # df.loc[df.FORM.str.match(expr), 'UPOS'] = 'NOM'

def is_comma_only_root_att(tree_df):
    # checks to see if the only tokens that attach to the root are commas.
    # If that is the case, do not fix commas in the tree, since no other tokens with attach to root
    # after the commas are fixed.
    tokens_attached_to_root = tree_df[tree_df.HEAD == 0].FORM.tolist()
    if all(token in [',', '،'] for token in tokens_attached_to_root):
        return True
    return False

def fix_conllx_sentences(conllx):
    
    fixed_df_list = []
    for tree_id in range(conllx.get_sentence_count()):
        tree_df = conllx.get_df_by_id(tree_id)
        if not is_comma_only_root_att(tree_df):
            tree_df = fix_sentence_commas(tree_df)
        # else:
        #     print(f"{conllx.file_path.name}\t{tree_id}")
        
        fix_tags_and_labels(tree_df)
        fixed_df_list.append(tree_df)
    return concat(fixed_df_list, axis=0)

if __name__ == '__main__':
    output_path = arguments['--output']

    if arguments['--conll']:
        conllx_path = pathlib.Path(arguments['--conll'])
    
        # conllx = read_conllx_file(conllx_full_path.parent, conllx_full_path.name)
        conllx = ConllxDf(file_path=conllx_path)
        # import pdb; pdb.set_trace()
        conllx.file_data = fix_conllx_sentences(conllx)
        # conllx.file_name = 'comma_test_data_fixed.conllx'
        
        if conllx_path == output_path: # same path, change name to avoid overwriting original
            file_name = f"{remove_file_name_extension(conllx.file_path.name)}_comma_fixed.conllx"
        else:
            file_name = ''
        conllx.write(pathlib.Path(output_path), file_name)
    elif arguments['--dir']:
        dir_path = pathlib.Path(arguments['--dir'])

        file_name_list = get_conll_files(dir_path, 'conllx')
        
        for file_name in file_name_list:
            print(f'Processing file {file_name}')
            conllx = ConllxDf(file_path=dir_path / file_name)
            conllx.file_data = fix_conllx_sentences(conllx)
            conllx.write(pathlib.Path(output_path), '')