
from dataclasses import dataclass
import os
from pathlib import Path
from typing import List


@dataclass
class DirectoryInformation():
    read_path: Path # of the parent directory
    write_path: Path # of the parent directory
    sub_dir_name_list: List[str] # list of sub-directories

def get_dir_names(data_path):
    if not os.path.isdir(Path(data_path)):
        raise FileNotFoundError(f'Directory not found: {data_path}')
    for dirpath, folders, _ in os.walk(data_path):
        print(f"Found directory: {dirpath}")
        return folders

def make_dir(dir_path: Path, raise_dir_exists_error=True):
    q = Path().absolute() / dir_path

    # Notify the user if a directory with the same experiment_id name exists,
    # but raise an error if directories within this directory exist.
    if raise_dir_exists_error:
        try:
            q.mkdir()
        except FileExistsError as exc:
            raise Exception(exc) from exc
    else:
        try:
            q.mkdir()
        except FileExistsError as exc:
            print(exc)

def create_directory_of_directories(dir_info: DirectoryInformation,
    raise_dir_exists_error: bool=True
    ) -> DirectoryInformation:
    
    dir_name_list = get_dir_names(dir_info.read_path)

    make_dir(dir_info.write_path, raise_dir_exists_error)
    for dir_name in dir_name_list:
        make_dir(dir_info.write_path/dir_name, raise_dir_exists_error)

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

def process_directory(dir_info, file_name_list, process_conllx):
    create_directory_of_directories(dir_info)
    # using dir_path and names, read files and process
    for dir_path in dir_info.sub_dir_name_list:
        # if file_name_list predefined don't fill it.
        file_name_list = file_name_list or get_file_names(dir_info.read_path/dir_path, "conllx")
        
        file_path = dir_info.read_path / dir_path
        for file_name in file_name_list:
            conllx = Conllx(file_name=file_name, file_path=file_path)
            conllx.read_file()
            
            process_conllx(conllx)
            
            conllx.file_path = dir_info.write_path/dir_path
            conllx.write_file()
        
        file_name_list = []

def remove_file_name_extension(file_name):
    # remove the extension, taking into account multiple . found in the name
    return '.'.join(file_name.split('.')[:-1])