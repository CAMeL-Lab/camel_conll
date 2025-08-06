import re
from camel_tools.utils.transliterate import Transliterator
from camel_tools.utils.charmap import CharMapper
# VRB and VRB-PASS
# sy
# st
# sn
# sA
# VRB-s VRB-PASS-s

# PRT
# ^([wlbf])\+?$
# PRT-one of the letters
# \SmA$
# PRT-mA

# The input word is assumed to follow the PATB tokenization scheme,
# with the + marker for all clitics


def get_pos_ex(word, pos):
    prepositions = r'^([A\>]mAm|[A\<]vr|[A\<]zA\'|bEd|byn|tjAh|tHt|tlw|H\*w|Hwl|HwAl[Yy]|Hyn|xlf|Dmn|Eqb|Ebr|mE|End|fwr|fwq|qbl|qbyl|qbAlp|qrb|[A\>]mvAl|[A\>]vnA\'|Dd|TwAl|EwD|Hsb|wfq|gyr|swY|[>A]bdA|mEA|Albtp|mvl|\$bh|nHw|dwn|ldY|xlAl|wrA\'|HyAl|jrA\'|wsT|rgm|dAxl|xArj)$'
    # CHANGE
    # yuval
    # pronouns = r'^(|\+)(hA|h|nA|hm|y|hmA|k|ny|km|kmA|kn|hn|AnA|nHn|Ant|Antn|AntmA|hw|hy)$'
    # nizar
    # pronouns = r'^\+?(hA|h|nA|hm|y|hmA|k|ny|km|kmA|kn|hn|AnA|nHn|Ant|Antn|AntmA|hw|hy)$'
    pronouns = r'^\+?(hA|h|nA|hm|y|hmA|k|ny|km|kmA|kn|hn|AnA|nHn|Ant|Antn|AntmA|hw|hy)\+?$'
    # standalone_pronouns = r'^(hm|hmA|hn|AnA|nHn|Ant|Antn|AntmA|hw|hy)$'
    # clitics_pronouns = r'^\+?(hA|h|nA|hm|y|hmA|k|ny|km|kmA|kn|hn)$'

    posEx = pos
    # if re.search(r'^Alt', word):
    #     return 'NOM-OH'
    if re.search(r'\d', word) and pos in ['NOM', 'PRT']:
        # check f-string python version. ask ossama
        return f'{pos}-NUM'
    elif re.search(r'^(sy|st|sn|sA)', word) and pos in ['VRB', 'VRB-PASS']:
        return pos + '-s'
    elif pos == 'PRT':
        # # added ? after the +
        # yuval, nizar
        # prt_re = re.search(r'^([wlbf])\+?$', word)
        prt_re = re.search(r'^\+?([wlbf])\+?$', word)
        if prt_re:
            return f'PRT-{prt_re.group(1)}'
        # yuval, nizar
        # elif re.search(r'\SmA$', word):
        elif re.search(r'[^\s+]mA\+?$', word):
            return 'PRT-mA'
        # yuval, nizar
        # elif re.search(r'^(fY|fy|mn|ElY|Ely|AlY|Aly|En|k\+)$', word):
        elif re.search(r'^(fY|fy|mn|ElY|Ely|AlY|Aly|En|k)\+?$', word):
            return 'PRT-PREP'
        # yuval, nizar
        # elif re.search(r'^(lA|lm|ln)$', word):
        elif re.search(r'^\+?(lA|lm|ln)\+?$', word):
            return 'PRT-NEG'
        # yuval, nizar
        # elif re.search(r'^[A\>\<]n$', word):
        elif re.search(r'^[A\>\<]n\+?$', word):
            return 'PRT-An'
        # nizar
        # elif re.search(r'^(qd|swf|s\+)$', word):
        elif re.search(r'^(qd|swf|s\+?)$', word):
            return 'PRT-V'

    elif pos == 'NOM':
        if re.search(prepositions, word):
            return 'NOM-PREP'
        elif re.search(pronouns, word):
            return 'NOM-PRON'
        else:
            # CHANGE
            al_nom_re = re.search(r'^Al(|\+)', word)
            # al_nom_re = re.search(r'^Al', word)
            if al_nom_re:
                posEx = f'Al-{posEx}'
            # CHANGE THIS AND THE ONE AFTER IT!
            # yuval
            # pron_re = re.search(r'(|\+)(At|An|p|y|wn|yn|A|w)$', word)
            # nizar
            # pron_re = re.search(r'(At|An|p|y|wn|yn|A|w)$', word)
            pron_re = re.search(r'(At|An|p|y|wn|yn|A|w)\+?$', word)
            if pron_re:
                # nizar
                # posEx = f'{posEx}-{pron_re.group(1)}'
                # yuval
                # posEx = f'{posEx}-{pron_re.group(2)}'
                posEx = f'{posEx}-{pron_re.group(1)}'
    elif pos == 'PNX':
        if re.search(r'^\.$', word):
            return 'PNX-DOT'
        elif re.search(r'^,$', word):
            return 'PNX-COMMA'
        elif re.search(r'^\"|\'$', word):
            return 'PNX-QUOTE'
        # LRB RRB?
        # no $ at the end?
        elif re.search(r'^\(|\)|-LRB-|-RRB-', word):
            # maybe PAREN is better?
            return 'PNX-PRN'
        elif re.search(r'^-$', word):
            return 'PNX-DASH'
        else:
            return 'PNX'
    # will change PROP to NOM for pos
    elif pos == 'PROP':
        # terrible addition
        if word == 'fxAmp':
            return 'NOM-WHAT'
        return 'NOM-PROP'
    return posEx


# print(get_pos_ex('sy}p', 'NOM'))
def set_df_xpos_to_catibex(df):
    mapper = CharMapper.builtin_mapper('ar2bw')
    transliterator = Transliterator(mapper)
    for index, row in df.iterrows():
        # print(row['XPOS'])
        # row['qXPOS'] = get_pos_ex(row['FORM'], row['UPOS'])
        temp_xpos = get_pos_ex(transliterator.transliterate(row['FORM']), row['UPOS'])
        df.loc[index, 'XPOS'] = temp_xpos
    # print(df)
    return df
