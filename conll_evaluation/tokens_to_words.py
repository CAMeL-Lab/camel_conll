"""
Combine tokens into words for evaluation

Also makes clitic checks. Ensures the token is actually a clitic and not composed only of pluses (i.e. +, +++)
"""

from typing import List
import re

def get_plus_toks_regex():
    # only composed of pluses
    return re.compile(r'^\++$')

def is_enclitic(tok, plus_toks=get_plus_toks_regex()):
    return tok.startswith('+') and not plus_toks.match(tok)

def is_proclitic(tok, plus_toks=get_plus_toks_regex()):
    return tok.endswith('+') and not plus_toks.match(tok)

def get_unsegmented_words(tokens: List[str]):
    words = []
    current_word = ''
    for i, token in enumerate(tokens):
        if is_proclitic(token):
            current_word += token.replace('+', '')
            try:
                next_token = tokens[i+1]
            except: # reached the end
                assert False, f'Last token is a proclitic: {token}. It should not be the last token in the sentence'
    
            assert not is_enclitic(next_token), f'{token} is followed by {next_token}; enclitic after proclitic'

        elif is_enclitic(token):
            if i == 0:
                assert not is_enclitic(token), f'First token is an enclitic {token}'

            current_word += token.replace('+', '')
            try:
                next_token = tokens[i+1]
            except: # reached the end
                words.append(current_word)
                current_word = ''
                continue
            if not is_enclitic(next_token):
                words.append(current_word)
                current_word = ''    
        else:
            current_word += token
            try:
                next_token = tokens[i+1]
            except: # reached the end
                words.append(current_word)
                current_word = ''
                continue
            if not is_enclitic(next_token):
                words.append(current_word)
                current_word = ''

    return words
