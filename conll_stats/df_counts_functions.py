from typing import List
from pandas import DataFrame, Series

from conll_stats.enum_classes import DeprelLabels, PosTags, LeadTypes

### base functions

def add_missing_columns(series: Series, column_values: List[str]):
    # used by get_column_value_counts.
    # updating series is a call by reference, hence no return value.
    
    for col_val in column_values:
        if col_val not in series:
            series[col_val] = 0

def get_column_value_counts(df: DataFrame, column_name: str, values: List[str]) -> Series:
    counts = df[column_name].value_counts()
    add_missing_columns(counts, values)
    return counts

def get_token_count(df: DataFrame) -> int:
    return df.shape[0]

def get_word_count(df: DataFrame, word_column: str='FORM') -> int:
    # excludes pro/enclitics, but not strings that contain the + sign i.e. +++
    # return df[~df[word_column].str.contains(r'^\+\w+$|^\w+\+$')].shape[0]
    # return df[~df[word_column].str.contains(r'^\+(\w|[\u0621-\u064A])+$|^(\w|[\u0621-\u064A])+\+$')].shape[0]
    return df[~df[word_column].str.contains(r'^\+(?:\w+|[،-٩]+)$|^(?:\w+|[،-٩]+)\+$')].shape[0]

def get_tokenized_word_count(df: DataFrame, word_column: str='FORM') -> int:
    """
    word: عِنْدَما
    tokens: عِنْدَ +ما
    tokenized word: عِنْدَ_+ما
    tokenized word count: only words that were tokenized (من is not a tokenized word)
    """
    forms = df[word_column]
    # replace tokens that are only pluses eg. + or +++ rather than li+
    tokens_without_plus = forms.str.replace(pat=r'^\++$', repl='PLUS_TOKEN', regex=True)
    # just tokens into a space-separated sentence
    sentence = ' '.join(list(tokens_without_plus))

    merged_tokens = sentence.replace(' +', '_+').replace('+ ', '+_')
    merged_tokens_series = Series(merged_tokens.split())

    return merged_tokens_series.str.contains('\+').sum()

def get_sentence_count(df: DataFrame) -> int:
        """Get the number of sentences in the CoNLL-U/X file.
        The beginning of each tree is extracted (ID = 1), then counted
        
        Returns:
            int: the number of sentences
        """
        return len(df[df['ID'] == 1].index)
    
def get_sentence_lengths(df: DataFrame) -> List[int]:        
    """Return the lengths of the sentences in the CoNLL-U/X file.

    Returns:
        List[int]: sentence lengths
    """
    # get the index of the first element of each tree (ID = 1),
    # decrement indices by 1 to get the last element from each tree.
    # the ID of the last element is equal to the length of each tree.
    last_items = list(df.iloc[df[df['ID'] == 1].index - 1]['ID'])
    # when decrementing, the first item in the list becomes the last item of the last tree.
    # remove it and place it at the end.
    return last_items[1:] + [last_items[0]]

################

### extending base functions. These functions are specific to our data.

def get_pos_tag_counts(df: DataFrame) -> Series:
    column_values = [ev.value for ev in PosTags]
    return get_column_value_counts(df, 'UPOS', column_values)
    
def get_deprel_label_counts(df: DataFrame) -> Series:
    column_values = [ev.value for ev in DeprelLabels]
    return get_column_value_counts(df, 'DEPREL', column_values)

def get_word_level_counts_series(df: DataFrame) -> Series:
    return Series({'word_count': get_word_count(df),
                'token_count': get_token_count(df),
                'tokenized_word_count': get_tokenized_word_count(df)})

def get_sentence_level_counts_series(df: DataFrame) -> Series:
    sent_count = get_sentence_count(df)
    sen_lengths = get_sentence_lengths(df)
    return Series({
        'sentence_count': sent_count,
        'max_sentence_length': max(sen_lengths),
        'min_sentence_length': min(sen_lengths),
        'mean_sentence_length': sum(sen_lengths) / len(sen_lengths),
    })


def get_leading_count_series(df: DataFrame) -> Series:
    # if the childs ID is less than its parent ID, then the child leads the relationship.
    counts = (df['ID'] < df['HEAD']).value_counts()
    counts.rename({False: 'P-C', True: 'C-P'}, inplace=True)
    
    column_values = [ev.value for ev in LeadTypes]
    
    add_missing_columns(counts, column_values)
    return counts

################