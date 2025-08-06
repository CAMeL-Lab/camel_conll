
# duplicates
# {'+mA': ['NOM', 'PRT'], 'k+': ['NOM', 'PRT'], '<n+': ['PRT', 'PROP']}

prt_token_pos_dict = {
    'أ+': ['PRT'],
    
    'ف+': ['PRT'],
    'و+': ['PRT'],
    
    'ب+': ['PRT'],
    'ك+': ['PRT'],
    'ل+': ['PRT'],
    
    'س+': ['PRT'],
    
    'لا+': ['PRT'],
    'ما+': ['PRT'],
    
    '+ني': ['NOM'],
    '+ي': ['NOM'],
    '+نا': ['NOM'],
    
    '+ك': ['NOM'],
    '+كما': ['NOM'],
    '+كم': ['NOM'],
    '+كن': ['NOM'],
    
    '+ه': ['NOM'],
    '+ها': ['NOM'],
    '+هما': ['NOM'],
    '+هم': ['NOM'],
    '+هن': ['NOM'],
    
    '+من': ['NOM'],
    '+ما': ['NOM', 'PRT'],
    '+لا': ['PRT'],
    '+م': ['NOM'],
    '+كو': ['NOM'],
    '+كي': ['NOM'],
    '+ش': ['PRT'],
    
    '+ج': ['NOM'],
    'ع+': ['PRT'],
    'ش+': ['NOM'],
    'ه+': ['NOM'],
}

def get_regex_expression_by_tag(tag=None):    
    x = [k for k, v in prt_token_pos_dict.items() if tag is None or tag in v]
    return '|'.join(x).replace('+', '\+')
    
if __name__ == '__main__':
    exp = get_regex_expression_by_tag('NOM')
    print(exp.split('|'))