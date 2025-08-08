"""Converts the POS tags and DEPREL labels to their Arabic equivalent.

Usage:
    catib_enrichment (-i <input> | --input=<input>)
        (-o <output> | --output=<output>)
        [-m <map_version> | --map_version=<map_version>]
    catib_enrichment (-h | --help)

Options:
    -i <input> --input=<input>
        A CoNLL-U/X file or a directory containing CoNLL-U/X files
    -o <output> --output=<output>
        The directory to fixed CoNLL files
    -m <map_version> --map_version=<map_version>
        tsv file containing POS and DEPREL mappings [default: 5]
    -h --help
        Show this screen.
"""
from pathlib import Path
import sys
import pandas as pd
from docopt import docopt

from conllx_df.conllx_df import ConllxDf
from utils.dir_utils import get_conll_files
from catib_enrichment.tree_functions import add_order, add_parent_details, get_token_details
from catib_enrichment.mapper import get_catib_plus, update_tree

arguments = docopt(__doc__)

def get_new_token_tag_and_label(token_details, sen_df, map_df, print_all_possibilities):
    try:
        if token_details.lex == 'ROOT':
            return '', ''
    except:
        import pdb; pdb.set_trace()
    # parent details and order required before getting catib plus feature values
    add_parent_details(sen_df, token_details)
    add_order(token_details)

    return get_catib_plus(token_details, map_df, 'POS', print_all_possibilities), get_catib_plus(token_details, map_df, 'REL', print_all_possibilities)

def get_new_tree_tags_and_labels(sen_df, map_df, print_all_possibilities=False):
    new_values = []
    # tokens
    for _, row in sen_df.iterrows():
        # token details
        token_details = get_token_details(sen_df, row['ID'])
        
        new_pos_value, new_rel_value = get_new_token_tag_and_label(token_details, sen_df, map_df, print_all_possibilities)

        if new_pos_value and new_rel_value:
            new_values.append({'new_upos': new_pos_value, 'new_deprel': new_rel_value})
    return new_values


def main():
    map_version = arguments['--map_version']
    input_dir = Path(arguments['--input'])
    output_dir = Path(arguments['--output'])

    files = get_conll_files(arguments['--input'])

    map_df = pd.read_csv(f'catib_enrichment/map_files/CATiB_plus_map_v{map_version}.tsv', sep='\t')

    # ensures that the exact_matches column is up to date
    # the exact_matches column counts the number of non-* values in each row
    features = ['lex', 'catib_pos', 'mada_pos', 'parent_lex', 'parent_catib_pos', 'parent_mada_pos', 'rel', 'order']
    map_df['exact_matches'] = 8 - (map_df[features] == '*').sum(axis=1)

    print_all_possibilities = True

    for file in files:
        print(file)
        conll = ConllxDf(input_dir / file)

        # sentences
        for sen_idx in range(conll.get_sentence_count()):
            sen_df = conll.get_df_by_id(sen_idx)
            # print(conll.get_comments_by_id(sen_idx)[0])
            new_values = get_new_tree_tags_and_labels(sen_df, map_df, print_all_possibilities)
            update_tree(sen_df, new_values)

        conll.write(Path(output_dir))

if __name__ == '__main__':
    main()