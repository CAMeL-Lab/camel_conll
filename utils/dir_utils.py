
import os
from typing import List

def get_files(input_path: str) -> List[str]:
    # return one or more file_paths in a list,
    # depending on whether a single file or a directory of files
    # has been passed.
    if os.path.isdir(input_path):
        return sorted([os.path.join(input_path,f) for f in os.listdir(input_path) 
            if os.path.isfile(os.path.join(input_path,f))])
    else:
        return [input_path]

def is_conll(f: str) -> bool:
    return f.endswith('.conllx') or f.endswith('.conllu')

def get_conll_files(input_arg: str) -> List[str]:
    ## checks whether input was a file or a directory
    all_files = [input_arg] if os.path.isfile(input_arg) else get_files(input_arg)
    return [file for file in all_files if is_conll(file)]

def remove_file_name_extension(file_name):
    # remove the extension, taking into account multiple . found in the name
    return '.'.join(file_name.split('.')[:-1])