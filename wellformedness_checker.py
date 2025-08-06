"""Checks a CoNLL-X file or directory of CoNLL-X files for different errors
to help with annotation.

Usage:
    text_to_conll_cli ((-c <input> | --conll=<input>) | (-d <input> | --dir=<input>))
        (-o <output> | --output=<output>)
        [-b <morphology_db_type> | --morphology_db_type=<morphology_db_type>]
    text_to_conll_cli (-h | --help)

Options:
    -c <input> --conll=<input>
        A CoNLL file
    -d <input> --dir=<input>
        A directory of CoNLL files
    -o <output> --output=<output>
        The directory to fixed CoNLL files
    -b <morphology_db_type> --morphology_db_type=<morphology_db_type>
        The morphology database to use; will use camel_tools built-in by default [default: r13]
    -h --help
        Show this screen.
"""
import pathlib
from typing import List
import pandas as pd
from docopt import docopt

from utils.analyzer import set_up_analyzer
from conllx_df.conllx_df import ConllxDf

from utils.dir_utils import get_file_names, remove_file_name_extension
from wellformedness.get_conllu_wellformedness_stats import save_stats
from wellformedness.clitic_check import clitic_checker
from wellformedness.common_functions import add_token_level_details, add_text_details
from wellformedness.conllx_check import conllx_checker
from wellformedness.element_check import element_checker
from wellformedness.form_pos_check import form_pos_checker
from wellformedness.pattern_check import pattern_checker
from wellformedness.mid_pnx_check import mid_pnx_checker
from wellformedness.pnx_position_check import pnx_checker
from wellformedness.projectivity_check import projective_checker
from wellformedness.root_check import root_checker
from wellformedness.deprel_check import deprel_checker

arguments = docopt(__doc__)

def get_sentence_errors(conllx_df):
    projectivity_errors = projective_checker(conllx_df)
    root_errors = root_checker(conllx_df)
    period_errors = mid_pnx_checker(conllx_df)
    conllx_errors = conllx_checker(conllx_df)
    
    return projectivity_errors + root_errors + period_errors + conllx_errors

def get_token_errors(conllx_df, analyzer):
    element_errors = element_checker(conllx_df)
    clitic_errors = clitic_checker(conllx_df)
    form_pos_errors = form_pos_checker(conllx_df, analyzer)
    pnx_errors = pnx_checker(conllx_df)
    pattern_errors = pattern_checker(conllx_df)
    children_deprel_errors = deprel_checker(conllx_df)
    
    return element_errors + clitic_errors + form_pos_errors + pnx_errors + pattern_errors + children_deprel_errors

def get_all_errors(conllx, analyzer, conllx_file_name) -> List[dict]:
    all_errors = []
    for idx in range(conllx.get_sentence_count()):
        conllx_df = conllx.get_df_by_id(idx)
        conllx_df.reset_index(drop=True, inplace=True)
        
        current_sentence_errors = []
        # append token errors
        token_errors = get_token_errors(conllx_df, analyzer)
        # print(sentence.text)
        current_sentence_errors += add_token_level_details(conllx_df, token_errors)
        # append sentence errors
        current_sentence_errors += get_sentence_errors(conllx_df)
        
        # text = conllx.get_comments_by_id(idx)[0] # the first comment is usually the text line
        text_line = conllx.get_text_line_by_id(idx)

        all_errors += [add_text_details(one_err, text_line, idx+1) for one_err in current_sentence_errors]
    return all_errors

def update_df_columns(all_errors, file_name):
    df = pd.DataFrame(all_errors)    
    
    # columns may be missing if either no token errors were encountered or sentence errors
    cols = ["flagged_issue", "sentence_number", "token_id", "form", "pos_tag", "label", "parent_id", "parent_form" ,"parent_pos_tag", "direction", "text"]
    df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=0)
    
    df = df[["flagged_issue", "sentence_number", "token_id", "form", "pos_tag", "label", "parent_id", "parent_form" ,"parent_pos_tag", "direction", "text"]]
    df['file_name'] = file_name
    return df

# TODO, generate correct number of words using a proper token check function
def get_conllx_counts(conllx) -> dict:
    sentence_count = conllx.get_sentence_count()
    token_count = conllx.df.shape[0]
    word_count = conllx.df[~conllx.df['FORM'].str.contains('\+')].shape[0]
    
    return {
        "sentence_count": sentence_count,
        "token_count": token_count, 
        "word_count": word_count
    }


def main():
    output_path = arguments['--output']
    morphology_db_type = arguments['--morphology_db_type']


    analyzer = set_up_analyzer(morphology_db_type)

    if arguments['--conll']:
        conll_path = pathlib.Path(arguments['--conll'])
        dir_path = conll_path.parent
        file_name_list = [conll_path.name]
    elif arguments['--dir']:
        dir_path = pathlib.Path(arguments['--dir'])
        file_name_list = get_file_names(dir_path, 'conllx')

    stats_dict_list = []
    # get errors then save errors per conllx file
    df_list = []
    for file_name in file_name_list:
        print(f'Processing file {file_name}')
        conllx = ConllxDf(file_path=dir_path / file_name)
        

        errors_and_stats = {
            "conllx_errors": get_all_errors(conllx, analyzer, file_name),
            "conllx_counts": get_conllx_counts(conllx)
            }
        
        stats_dict_list.append({'file_name': remove_file_name_extension(file_name), 
                    'sentence_count': errors_and_stats["conllx_counts"]["sentence_count"],
                    'tok_count': errors_and_stats["conllx_counts"]["token_count"],
                    'word_count': errors_and_stats["conllx_counts"]["word_count"]})

        df = update_df_columns(errors_and_stats["conllx_errors"], remove_file_name_extension(file_name))
        df_list.append(df)
        # will save errors per file in separate tsv files.
        df.to_csv(f"{output_path}/{remove_file_name_extension(file_name)}.tsv", sep='\t', index=False)
    
    save_stats(pathlib.Path(output_path), dir_path.name, df_list, stats_dict_list)

if __name__ == '__main__':
    main()