"""
6) Valid quadruples
    - (POSparent, DEPREL, POSchild, arc_direction)
        should be valid

from df
get child pos
get child form
get deprel


get parent pos
get parent form
get direction
"""
import re
from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.transliterate import Transliterator
import numpy as np
import pickle
import pandas as pd
from pandas import DataFrame
# from wellformedness.clitic_check import is_clitic, is_enclitic, is_proclitic
from ..clitic_check import is_clitic, is_enclitic, is_proclitic

from ..common_functions import get_sentence_column_data

def get_token_by_id(id: int, df: DataFrame) -> dict:
    assert type(id) == int, 'Invalid id type; make sure it is an int'
    
    return df[df["ID"] == id].to_records('dict')[0]

def get_new_pnx_name(pnx_token_form: str, direction: str, upos: str):
    # for roman script
    # sourcery skip: remove-duplicate-key
    reg = r"(( *[؟؛!.;?!] *)+)"

    pnx_types = {
        'B': re.compile(r'[.,;:?!؟،؛!.%\)»\]}>]+'), # parent should be backwards
        'A': re.compile(r'[\(«\[{<]+'), # parent should be forwards (after)
        # 'R': (')', 'P-C'), # parent should be backwards
        'AB': re.compile(r'["\'_\-/\\+=\—\–\*\^~♫]+') # parent can be either
    }
    for k, v in pnx_types.items():
        # if pnx_token_form in v[0] and v[1] in ['BOTH', direction]:
        if v.match(pnx_token_form) and upos == 'PNX':
            return f'{upos}-{k}'
    return upos

def get_new_clitic_name(form: str, upos: str):
    if is_clitic(form) and is_proclitic(form):
        return f'{upos}#'
    elif is_clitic(form) and is_enclitic(form):
        return f'#{upos}'
    else:
        return upos

def update_prt_upos(df):
    df['UPOS_child'] = df.apply(lambda row: get_new_pnx_name(row['FORM_child'], row['direction'], row['UPOS_child']), axis=1)
    df['UPOS_parent'] = df.apply(lambda row: get_new_pnx_name(row['FORM_parent'], row['direction'], row['UPOS_parent']), axis=1)

def update_clitic_upos(df):
    df['UPOS_child'] = df.apply(lambda row: get_new_clitic_name(row['FORM_child'], row['UPOS_child']), axis=1)
    df['UPOS_parent'] = df.apply(lambda row: get_new_clitic_name(row['FORM_parent'], row['UPOS_parent']), axis=1)

def get_patterns_from_df(df): # for each dependency tree
    # df is the child dataframe
    
    # get parent dataframe
    parent_id_list = get_sentence_column_data(df, "HEAD")
    parent_df = df[df['ID'].isin(parent_id_list)]

    # merge parent and child on parent ID and child HEAD
    merged = pd.merge(df, parent_df, how='left', left_on='HEAD', right_on='ID',
                    suffixes=('_child', '_parent'))
    fix_after_merge(merged)

    add_examples_to_df(merged)
    
    update_prt_upos(merged)
    update_clitic_upos(merged)
    
    

    return merged

def add_examples_to_df(merged):
    merged['surface_order_parent/child_forms'] = np.where(merged['direction'] == 'P-C',
        merged['FORM_parent'] + ' ... ' + merged['FORM_child'],
        merged['FORM_child'] + ' ... ' + merged['FORM_parent'])

    mapper = CharMapper.builtin_mapper('bw2ar')
    transliterator = Transliterator(mapper)

    merged['arabic_example_surface_order_parent/child_forms'] = merged.apply(lambda row: transliterator.transliterate(row['surface_order_parent/child_forms']), axis=1)
    
    # return merged

def fix_after_merge(merged):
    merged.drop(['HEAD_parent', 'DEPREL_parent'], axis=1, inplace=True)
    # merged['ID_parent'] = merged['ID_parent'].fillna(0).astype(int)
    merged['FORM_parent'] = merged['FORM_parent'].fillna('---')
    merged['UPOS_parent'] = merged['UPOS_parent'].fillna('ROOT')

    merged['direction_int'] = merged['ID_parent'] - merged['ID_child']
    merged['direction'] = np.where(merged['direction_int'] > 0, 'C-P', 'P-C')
    # return merged

if __name__ == '__main__':
    
    #################################
    # Used to generate pickle file for the sentence list of catib train
    #################################
    # patb_train_file_path = './data/catib'
    # patb_train_file_name = 'catib.train.v2.11062020.conllx'
    
    # conllx = Conllx(file_name=patb_train_file_name, file_path=patb_train_file_path)
    # conllx.read_file()
    
    # sentence_list = conllx.conllx_to_sentence_list()
    
    # with open('./data/catib_train_sen_list.pkl', 'wb') as f:
    #     pickle.dump(sentence_list, f)
    
    #################################
    # Used to read the stored sentence list pickle file
    ################################
    with open('./data/patterns/catib_train_sen_list.pkl', 'rb') as f:
        pickled_sentence_list = pickle.load(f)
    
    
    ################################
    # Preparing the tuple pattern data
    ################################
    mapper = CharMapper.builtin_mapper('bw2ar')
    transliterator = Transliterator(mapper)
    
    df_list = []
    for sentence in pickled_sentence_list:
        df = sentence.dependency_tree.copy()[['ID', 'FORM', 'UPOS', 'HEAD', 'DEPREL']]
        df['HEAD'] = df['HEAD'].astype(int)
        df['full_sentence_arabic'] = transliterator.transliterate(' '.join(list(df['FORM'])))
        
        df_list.append(get_patterns_from_df(df))
        
    
    full_df = pd.concat(df_list)
    print(full_df.columns)

    full_df.to_csv('./data/patterns/pattern_list_full_sent.tsv', sep='\t', index=False)