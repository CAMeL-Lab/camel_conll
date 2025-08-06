"""
6) Valid quadruples
    - (POSparent, DEPREL, POSchild, arc_direction)
        should be valid
"""

import pprint as pp
import pandas as pd
from .common_functions import get_sentence_column_data, get_token_details
# from wellformedness.patterns_list import get_patterns_list
# from wellformedness.token_tuple_utils.get_tuple_patterns import fix_after_merge, update_clitic_upos, update_prt_upos
from .token_tuple_utils.get_tuple_patterns import fix_after_merge, update_clitic_upos, update_prt_upos

def get_patterns_list():  # sourcery skip: use-fstring-for-concatenation
    pattern_data = read_pattern_file()
    
    # get only valid patterns
    pattern_data = pattern_data[pattern_data['Final'] == 'OK']
    
    patterns = pattern_data['UPOS_child'] + "_" + pattern_data['DEPREL_child'] + '_' + pattern_data['UPOS_parent'] + '_' + pattern_data['direction']
    return list(patterns)

def update_patterns(patterns):
    patterns = patterns.str.replace('PROP', 'NOM')
    patterns = patterns.str.replace('FOREIGN', 'NOM')
    patterns = patterns.str.replace('VRB-PASS', 'VRB')
    return patterns

def pattern_checker(main_df):
    df = main_df.copy()
    # combine UPOS_child_DEPREL_child_UPOS_parent
    parent_list = [get_token_details(df, x) for x in list(get_sentence_column_data(df, "HEAD"))]
    parent_df = pd.DataFrame(parent_list)
    # import pdb; pdb.set_trace()
    
    df['ID'] = df['ID'].astype(int)
    df['HEAD'] = df['HEAD'].astype(int)
    merged = pd.merge(df, parent_df, how='left', left_index=True, right_index=True,
                    suffixes=('_child', '_parent'))
    # merged = pd.merge(df, parent_df, how='left', left_on='HEAD', right_on='ID',
    #                 suffixes=('_child', '_parent'))

    fix_after_merge(merged)
    update_prt_upos(merged)
    update_clitic_upos(merged)
    patterns = merged['UPOS_child'] + '_' +  merged['DEPREL_child'] + '_' + merged['UPOS_parent'] + '_' + merged['direction']
    patterns = update_patterns(patterns)
    
    patterns_df = pd.DataFrame({
        'token_id': merged['ID_child'],
        'UPOS_child': merged['UPOS_child'], 
        'UPOS_parent': merged['UPOS_parent'], 
        'patterns': patterns})
    
    valid_patterns_list = get_patterns_list()
    err_tokens = patterns_df[patterns_df['patterns'].isin(valid_patterns_list) == False]
    err_patterns = []
    for _, row in err_tokens.iterrows():
        temp_err = {
            "token_id": row.token_id,
            "pos_tag": row["UPOS_child"],
            "parent_pos_tag": row['UPOS_parent'],
            "flagged_issue": 'FLAG_UNK_SYNTAX_PATTERN'
        }
        err_patterns.append(temp_err)
    return err_patterns


def read_pattern_file():
    return pd.read_csv(
        'data/patterns/patb123_patterns_v4.tsv',
        header=0,
        usecols=list(range(1, 12)),
        sep='\t',
    )

# sourcery skip: use-fstring-for-concatenation
if __name__ == '__main__':
    # this code block imitates the get_patterns_list function above
    pattern_data = read_pattern_file()
    pattern_data = pattern_data[pattern_data['Final'] == 'OK']
    
    patterns = pattern_data['UPOS_child'] + "_" + pattern_data['DEPREL_child'] + '_' + pattern_data['UPOS_parent'] + '_' + pattern_data['direction']
    pp.pprint(list(patterns))

