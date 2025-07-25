
from dataclasses import dataclass
import os
from pathlib import Path

def get_file_names(data_path, endswith=''):
    ret_files = []
    if not os.path.isdir(Path(data_path)):
        raise FileNotFoundError(f'Directory not found: {data_path}')
    for dirpath, _, files in os.walk(data_path):
        print(f"Found directory: {dirpath}")

        for file_name in files:
            ret_files.append(file_name)
        
        if 'Icon\r' in ret_files:
            ret_files.remove('Icon\r')
        if '.DS_Store' in ret_files:
            ret_files.remove('.DS_Store')
        
        if endswith:
            ret_files = [f_name for f_name in ret_files if f_name.endswith(endswith)]
        # done within the os.walk for loop so 
        # it doesn't traverse subdirectories
        return ret_files

def remove_file_name_extension(file_name):
    # remove the extension, taking into account multiple . found in the name
    return '.'.join(file_name.split('.')[:-1])