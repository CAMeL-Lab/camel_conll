# number of relations a parent can have with children
# eg: a parent can have at most 1 child with a SBJ relation
# from wellformedness.common_functions import get_children_ids_of
from .common_functions import get_children_ids_of
from pandas import Series

# MOD, OBJ, and --- can be any number, and so they aren't included here
# TPC could be multiple, so this is a strict check.
REL_COUNTS = {
    'IDF': 1,
    'TPC': 1,
    'SBJ': 1,
    'TMZ': 1,
    'PRD': 1,
}


def get_deprel_errors(conll_id, deprel_series):
    return [
        {
            'token_id': conll_id,
            "flagged_issue": "FLAG_MULTIPLE_DEPREL_LABELS",
        }
        for deprel, d_count in deprel_series.items()
        if deprel in REL_COUNTS
        and REL_COUNTS[deprel] < d_count
    ]        

def get_column_counts_by_id(df, id_list, column_name) -> Series:
    return df[(df['ID'].isin(id_list))][column_name].value_counts()

def deprel_checker(df):
    err_list = []
    for i, row in df.iterrows():
        child_id_list = get_children_ids_of(row['ID'], df)
        deprel_series = get_column_counts_by_id(df, child_id_list, 'DEPREL')
        # if not deprel_series.empty:
        err_list += get_deprel_errors(row['ID'], deprel_series)
    return err_list