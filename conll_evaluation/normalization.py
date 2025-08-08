

from camel_tools.utils.normalize import normalize_alef_ar as alef
from camel_tools.utils.normalize import normalize_alef_maksura_ar as yeh
from camel_tools.utils.normalize import normalize_teh_marbuta_ar as teh


# ..,;:?!؟،؛!.
punctuation_map = {
    '.': '.',
    '،': ',',
    '؛': ';',
    '؟': '?',
    '!': '!',
}

numbers_map = {
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
}

maps = {
    'punctuation': punctuation_map,
    'numbers': numbers_map,
}

def bw2ar_map_lines(conll_df, map_name):
    selected_map = maps[map_name]
    conll_df.FORM = conll_df.FORM.map(selected_map).fillna(conll_df.FORM)

def normalize_alef_yeh_ta_line(line):
    return alef(yeh(teh(line)))

def normalize_alef_yeh_ta(df):
    df.FORM = df.FORM.apply(normalize_alef_yeh_ta_line)

def transliterate_and_normalize(arguments, gold_conllx, parsed_conllx):
    if arguments['--transliterate_pnx']:
        bw2ar_map_lines(gold_conllx.df, 'punctuation')
        bw2ar_map_lines(parsed_conllx.df, 'punctuation')
    if arguments['--transliterate_num']:
        bw2ar_map_lines(gold_conllx.df, 'numbers')
        bw2ar_map_lines(parsed_conllx.df, 'numbers')
    if arguments['--normalize_alef_yeh_ta']:
        normalize_alef_yeh_ta(gold_conllx.df)
        normalize_alef_yeh_ta(parsed_conllx.df)