import pandas as pd

def get_pattern_counts(df):
    return df.groupby(['UPOS_child', 'UPOS_parent', 'DEPREL_child', 'direction']).UPOS_parent.agg('count').to_frame('counts').reset_index()

def get_example_counts(df):
    return df.groupby(['UPOS_child', 'UPOS_parent', 'DEPREL_child', 'direction', 'surface_order_parent/child_forms', 'arabic_example_surface_order_parent/child_forms']).UPOS_child.agg('count').to_frame('example_freq').reset_index()

def get_example_frequncy(examples_df):
    return examples_df.loc[examples_df.groupby(['UPOS_child', 'UPOS_parent', 'DEPREL_child', 'direction'])['example_freq'].idxmax()].reset_index(drop=True)

def add_example_frequency(df, examples_df):
    return pd.merge(df, examples_df,  how='left', on=['UPOS_child', 'UPOS_parent', 'DEPREL_child', 'direction'])

if __name__ == '__main__':
    
    df = pd.read_csv('./data/patterns/pattern_list_full_test.tsv', sep='\t')
    # gets the counts of the quadruples.
    # pattern_count = df[['UPOS_child', 'UPOS_parent', 'DEPREL_child', 'direction']].value_counts()
    pattern_counts = get_pattern_counts(df)
    
    # example_counts = get_example_counts(df)
    example_counts = get_example_frequncy(get_example_counts(df))
    full_stats = add_example_frequency(pattern_counts, example_counts)
    full_stats.to_csv('./data/patterns/pattern_list_stats_wo_sent.tsv', sep='\t')