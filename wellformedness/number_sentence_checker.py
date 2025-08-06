""" NOTE: this script was used for religious texts, and is currently not being used.

Checks if the line starts/ends with a number, primarily used for religious texts

if it:
    starts with a number
        check if the number connects to root with a flat label
    ends with ( number )
        check if they connect to one another, eventually to root, all flat labels
"""

def starts_with_num(df):
    return (df['FORM'].iloc[0]).isdigit()

def ends_with_paren_num(df):
    # TODO: refactor
    # locations of the digit and parens in the dataframe (last 3 tokens)
    digit_loc = -2
    closing_loc = -1
    opening_loc = -3
    
    # digit is a digit, connects to root and is flat
    digit_id = df['ID'].iloc[digit_loc]
    digit = df['FORM'].iloc[digit_loc]
    digit_parent = df['HEAD'].iloc[digit_loc]
    digit_label = df['DEPREL'].iloc[digit_loc]
    digit_connects_to_root = digit.isdigit() and digit_parent == 0 and digit_label == '---'
    
    # open/close parens are parens, connect to digit, and are MOD
    closing_paren = df['FORM'].iloc[closing_loc]
    closing_parent = df['HEAD'].iloc[closing_loc]
    closing_paren_label = df['DEPREL'].iloc[closing_loc]
    
    opening_paren = df['FORM'].iloc[opening_loc]
    opening_parent = df['HEAD'].iloc[opening_loc]
    opening_paren_label = df['DEPREL'].iloc[opening_loc]
    
    parens_connect_to_digit = closing_paren == ')' and opening_paren == '(' and\
        closing_parent == opening_parent == digit_id and\
            closing_paren_label == opening_paren_label == 'MOD'

    return digit_connects_to_root and parens_connect_to_digit

def number_sentence_checker(df):
    if starts_with_num(df) or (df.shape[0] and ends_with_paren_num(df)):
        return []
    else:
        return [{"flagged_issue": "FLAG_SENTENCE_NUM"}]