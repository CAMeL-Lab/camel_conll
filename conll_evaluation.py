"""
Evaluates a parsed CoNLL file against gold or 
    a directory containing parsed CoNLL files against a gold directory.

Usage:
    evaluate_conllx_driver ((-g <gold> | --gold=<gold>) (-p <parsed> | --parsed=<parsed>))
        [-x | --transliterate_pnx]
        [-n | --transliterate_num]
        [-a | --normalize_alef_yeh_ta]
        [((-o <output_path> | --output_path=<output_path>) <output_file_name>)]
    evaluate_conllx_driver (-h | --help)

Options:
    -g <gold> --gold=<gold>
        The gold CoNLL file or directory of files.
    -p <parsed> --parsed=<parsed>
        The parsed CoNLL file or directory of files.
    -x --transliterate_pnx
        Transliterate punctuation to Roman script (punctuation will always match regardless of script)
    -n --transliterate_num
        Transliterate numbers to Roman script (numbers will always match regardless of script)
    -a --normalize_alef_yeh_ta
        Normalizes alef, alef maksura, and teh marbuta
    -o <output_path> --output_path=<output_path>
        Output path to save the tsv counts file. If not specified, output will be printed to stdout.
    <output_file_name>
        The name of the output file (a tsv extension will be added automatically).
    -h --help
        Show this screen.

"""

import pathlib
from docopt import docopt
from pandas import DataFrame

from conllx_df.conllx_df import ConllxDf

from utils.dir_utils import get_conll_files
from conll_evaluation.tree_evaluation import compare_conll_trees
from conll_evaluation.normalization import transliterate_and_normalize

arguments = docopt(__doc__)

def get_synced_file_names(gold_files, parsed_files):
    gold_file_names = [pathlib.Path(file_path).name for file_path in gold_files]
    parsed_file_names = [pathlib.Path(file_path).name for file_path in parsed_files]
    tuple_list = []
    for gold_file in gold_file_names:
        parsed_file = [x for x in parsed_file_names if x == gold_file][0]
        tuple_list.append((gold_file, parsed_file))
    return tuple_list

def get_file_path_details(file_path):
    full_path = pathlib.Path(file_path)
    dir_path = full_path.parent
    file_name = full_path.name
    return dir_path, file_name

def main():
    gold_files = get_conll_files(arguments["--gold"])
    parsed_files = get_conll_files(arguments["--parsed"])

    try:
        tuple_list = get_synced_file_names(gold_files, parsed_files)
    except:
        raise ValueError('File names should be similar.')
    gold_path = pathlib.Path(gold_files[0]).parent
    parsed_path = pathlib.Path(parsed_files[0]).parent


    # reading files and storing scores for each file
    tree_counts_list = []
    tree_matches_list = []
    alignment_numbers_list = []
    num_sentences_list = []

    conll_scores_list = []
    for gold_file, parsed_file in tuple_list:
        gold_conllx = ConllxDf(gold_path / gold_file)
        parsed_conllx = ConllxDf(parsed_path / parsed_file)

        transliterate_and_normalize(arguments, gold_conllx, parsed_conllx)
        
        conll_scores = {
            'file_name': '.'.join(gold_file.split('.')[:-1]),
            **compare_conll_trees(gold_conllx, parsed_conllx)
        }
        conll_scores_list.append(conll_scores)

    scores_df = DataFrame(conll_scores_list).round(3)

    ## save to file or print to stdout.
    if arguments['--output_path']:
        print(f"results saved in {arguments['<output_file_name>']}.tsv")
        scores_df.to_csv(f"{arguments['--output_path']}/{arguments['<output_file_name>']}.tsv", sep='\t', index=False)
    else:
        print(scores_df)

if __name__ == '__main__':
    main()