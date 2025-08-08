from dataclasses import asdict, dataclass
import pandas as pd

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


def replace_stars(temp_choices, details_dict, current_key):
    for idx, row in temp_choices.iterrows():
        for col_name, col_value in row.items():
            if col_value == '*':
                temp_choices.loc[idx, col_name] = details_dict[col_name]

def match_anything(rel_choices, k):
    unique_vals = rel_choices[k].unique()
    if len(unique_vals) == 1 and unique_vals[0] == '*':
        return True
    return False

def get_catib_plus(
        details: SentenceToken,
        df_map,
        target_field,
        print_all_possibilities
    ):
    """
    
    2	ل+	ل+	PRT	_	ud=ADP|pos=prep|prc3=0|prc2=0|prc1=0|prc0=na|per=na|asp=na|vox=na|mod=na|gen=na|num=na|stt=na|cas=na|enc0=0|rat=na|token_type=prc1	1	PRD	_	_
    3	أحد	أحد	NOM	_	ud=NOUN|pos=noun|prc3=0|prc2=0|prc1=0|prc0=0|per=na|asp=na|vox=na|mod=na|gen=m|num=s|stt=c|cas=g|enc0=0|rat=i|token_type=baseword	2	OBJ	_	_
    """
    # details = SentenceToken(token_id=2, lex='أخضر', catib_pos='NOM', mada_pos='adj', parent_id=1, parent_lex='مكتبة',
    #                      parent_catib_pos='NOM', parent_mada_pos='noun', rel='MOD', order='P-C')
    
    # POS or REL in the map file
    rel_choices = df_map[df_map['target_field'] == target_field]
    
    details_dict = details.dict()
    # a dict where key is each feature we have, and value is a Series
    column_match_values = {}
    for k, v in details_dict.items():
        # return True/False when feature k is either v or *
        # ex: if k: v i lex: TAlb, we do not have a lex in the map file with that,
        # so rows with * will return True, rows with things like bAt and sAr will return False
        column_match_values[k] = (rel_choices[k] == v) | (rel_choices[k] == '*')
    
    # new_df contains the boolean values for each row. We take the sum of Trues to see
    # which rows match the most.
    new_df = pd.DataFrame.from_dict(column_match_values, orient='index').transpose()
    new_df['match_sum'] = new_df.sum(axis=1)

    # Take df indices to extract top matches, by token values and *
    indices_of_best_matches = new_df[new_df.match_sum == new_df.match_sum.max()].index
    matched = df_map.iloc[indices_of_best_matches]

    # if there were no valid matches except for UNK match, top_choices only contain the UNK match
    top_choices = matched[matched.exact_matches == matched.exact_matches.max()]

    if print_all_possibilities and top_choices.shape[0] > 1:
        return '|'.join(top_choices.target_value_long.unique())
    return top_choices.sort_values(by='index').iloc[0].target_value_long
    
def update_tree(sen_df, new_values):
    assert sen_df.shape[0] == len(new_values)
    for i, row in sen_df.iterrows():
        try:
            new_upos = new_values[row['ID']-1]['new_upos']
            new_deprel = new_values[row['ID']-1]['new_deprel']
            if row['UPOS'] != new_upos:
                # sen_df.loc[i, 'UPOS'] = f"{sen_df.loc[i, 'UPOS']}|{new_upos}"
                sen_df.loc[i, 'UPOS'] = new_upos
            if row['DEPREL'] != new_deprel:
                # sen_df.loc[i, 'DEPREL'] = f"{sen_df.loc[i, 'DEPREL']}|{new_deprel}"
                sen_df.loc[i, 'DEPREL'] = new_deprel
        except:
            import pdb; pdb.set_trace()

if __name__ == '__main__':
    """
    20	و+	و+	PRT	_	ud=CCONJ|pos=conj|prc3=0|prc2=0|prc1=0|prc0=na|per=na|asp=na|vox=na|mod=na|gen=na|num=na|stt=na|cas=na|enc0=0|rat=na|token_type=prc2	14	MOD	_	_
    23	سمينه	سمينه	NOM	_	ud=PROPN|pos=noun_prop|prc3=0|prc2=0|prc1=0|prc0=0|enc0=0|asp=na|vox=na|mod=na|gen=m|num=s|stt=i|cas=u|per=na|rat=i|token_type=baseword	20	OBJ	_	_
    

    سمينه
    NOM
    noun_prop
    و+
    PRT
    conj
    OBJ
    P-C
    """
    df_map = pd.read_csv('data/CATiB_plus_map.tsv', sep='\t')

    token_details = SentenceToken(23, 'سمينه', 'NOM', 'noun_prop', 20, 'و+', 'PRT', 'conj', 'OBJ', 'P-C')

    new_pos = get_catib_plus(token_details, df_map, 'POS', True)
    new_rel = get_catib_plus(token_details, df_map, 'REL', True)
    import pdb; pdb.set_trace()