"""
Conll counts CLI.

Usage:
    counts_main (-i <input> | --input=<input>)
                [-w | --words]
                [-s | --sentences]
                [-p | --pos_tags]
                [-d | --deprel_labels]
                [-l | --leading]
                [((-o <output_path> | --output_path=<output_path>) <output_file_name>)]
    counts_main (-h | --help)

Options:
    -i <input> --input=<input>
        A CoNLL-U/X file or a directory containing CoNLL-U/X files
    
    Flags that specify which counts to produce (default: all):
        -w --words
            get word-level counts (words, tokens, and tokenized words)
        -s --sentences
            get sentence-level counts (sentence count, and min/mean/max sentence lengths)
        -p --pos_tags
            get POS/CPOSTAG column counts
        -d --deprel_labels
            get DEPREL column counts
        -l --leading
            get the counts for P-C and C-P (child-leading vs parent-leading)

    -o <output_path> --output_path=<output_path>
        Output path to save the tsv counts file. If not specified, output will be printed to stdout.
    <output_file_name>
        The name of the output file (a tsv extension will be added automatically).
    -h --help
        Show this screen.
"""
from typing import Callable, List, Set
from pandas import concat, DataFrame, Series
from docopt import docopt

from conllx_df.conllx_df import ConllxDf

from conll_stats.enum_classes import DataFrameStringHeaders, DeprelLabels, PosTags, LeadTypes, SentenceLevelHeaders, WordLevelHeaders
from conll_stats.df_counts_functions import get_deprel_label_counts, get_leading_count_series, get_pos_tag_counts, get_word_level_counts_series, get_sentence_level_counts_series
from utils.dir_utils import get_conll_files
from utils.df_utils import set_numeric_columns_to_int, update_column_order
arguments = docopt(__doc__)

def get_flag_functions(arguments) -> List[Callable]:
    flags_to_item_map = {
        '--pos_tags': get_pos_tag_counts,
        '--deprel_labels': get_deprel_label_counts,
        '--words': get_word_level_counts_series,
        '--sentences': get_sentence_level_counts_series,
        '--leading': get_leading_count_series,
    }
    
    # gets values from flags_to_item_map if user selected flags,
    # otherwise return all of the above values.
    return [flags_to_item_map[k] for k in arguments if k in flags_to_item_map and arguments[k]]\
            or list(flags_to_item_map.values())

def get_file_counts(conll_df: DataFrame, flag_functions: List[Callable]) -> DataFrame:
    """Get counts of the selected flags.
    
    If POS and/or DEPREL labels are specified, add missing columns.

    Args:
        conll_df (DataFrame): The DataFrame to get counts from
        flags (List[Callable]): Functions of the desired flags

    Returns:
        DataFrame: counts of the desired flags
    """
    series_stats_list = []
    for fn in flag_functions:
        series_stats_list.append(fn(conll_df))

    return DataFrame(concat(series_stats_list)).transpose()

def get_full_column_list():
    column_lists = [
        [ev.value for ev in DataFrameStringHeaders],
        [ev.value for ev in WordLevelHeaders],
        [ev.value for ev in SentenceLevelHeaders],
        [ev.value for ev in PosTags],
        [ev.value for ev in DeprelLabels],
        [ev.value for ev in LeadTypes],
    ]
    
    # return single_columns + pos_tags + deprel_labels
    return [header for sublist in column_lists for header in sublist]

def adjust_df(df: DataFrame, string_columns: Set[str], full_column_list: List[str]) -> DataFrame:
    """_summary_

    Args:
        df (DataFrame): _description_
        string_columns (:obj:`Set`[:obj:`str`]): _description_

    Returns:
        DataFrame: _description_
    """
    df.reset_index(inplace=True, drop=True)
    df = set_numeric_columns_to_int(df, string_columns)
    
    return update_column_order(df, full_column_list)

def main():
    ## get file(s) and flag functions
    files = get_conll_files(arguments['--input'])
    flag_functions = get_flag_functions(arguments)

    ## set up counts DataFrame.
    df = DataFrame()
    for file in files:
        conll = ConllxDf(file)
        file_df = get_file_counts(conll.df, flag_functions)
        file_df['file_name'] = file.split('/')[-1]
        df = concat([df, file_df])

    df = adjust_df(df, {ev.value for ev in DataFrameStringHeaders}, get_full_column_list())

    ## save to file or print to stdout.
    if arguments['--output_path']:
        df.to_csv(f"{arguments['--output_path']}/{arguments['<output_file_name>']}.tsv", sep='\t', index=False)
    else:
        print(df)

if __name__ == '__main__':
    main()