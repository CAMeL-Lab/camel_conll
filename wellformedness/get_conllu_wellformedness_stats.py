import pathlib
from typing import List
import pandas as pd

from utils.dir_utils import remove_file_name_extension

ERR_LIST = [
    "FLAG_ENCLITIC",
    "FLAG_PROCLITIC",
    "FLAG_ID_OR_HEAD",
    "FLAG_MULTIPLE_DEPREL_LABELS",
    "FLAG_CATIB_TAGS",
    "FLAG_DEPREL_LABELS",
    "FLAG_FORM_OOV",
    "FLAG_FORM_POS_MISMATCH",
    "FLAG_MID_PNX_ATT",
    "FLAG_SENTENCE_NUM",
    "FLAG_UNK_SYNTAX_PATTERN",
    "FLAG_PNX_POSITION",
    "FLAG_NONPROJECTIVE",
    "FLAG_ROOT_ATT",
    ]

def get_flagged_issue_count(df):
    # print(flagged_issue_counts)
    # flagged_issue_counts = flagged_issue_counts + df['flagged_issue'].value_counts()
    # print(flagged_issue_counts)
    # return df['flagged_issue'].value_counts()
    issues_df = df['flagged_issue'].value_counts().to_frame().reset_index()
    return issues_df.rename(columns={'index':'flagged_issue', 'flagged_issue':'count'})

def get_df_list(dir_path: pathlib.Path, file_name_list: List[str]):
    df_list = []
    for file_name in file_name_list:
        df = pd.read_csv(dir_path / file_name, sep='\t')
        df['file_name'] = remove_file_name_extension(file_name)
        df_list.append(df)
    return df_list

def add_missing_error_types(df_err_per_file, ERR_LIST):
    for ERR in ERR_LIST:
        if ERR not in df_err_per_file.columns:
            df_err_per_file[ERR] = 0
    
    new_column_order = ["file_name"] + ERR_LIST + ["sentence_count", "tok_count", "word_count"]
    df_err_per_file = df_err_per_file.reindex(new_column_order, axis=1)
    return df_err_per_file

def save_stats(dir_path, stats_name, df_list, stats_dict_list=None):
    df = pd.concat(df_list)
    
    # move filename to beginning
    cols = list(df)
    cols.insert(0, cols.pop(cols.index('file_name')))
    df = df.loc[:, cols]
    
    # buggy
    # drop OOV except if a * exists in form
    # df = df.drop(df[(df['flagged_issue'] == 'FLAG_FORM_OOV') & ~(df['form'].str.contains('\*'))].index)
    # df_err_per_file = df.groupby(['file_name', 'flagged_issue']).size().to_frame('flagged_issue_count')
    df_err_per_file = df.groupby(['file_name', 'flagged_issue']).size().unstack().reset_index().fillna(0)
    if stats_dict_list:
        df_stats = pd.DataFrame(stats_dict_list)
        df_err_per_file = df_err_per_file.merge(df_stats, how='outer', on='file_name')
    df_err_per_file = add_missing_error_types(df_err_per_file, ERR_LIST)
    
    df_flagged_issue_count = get_flagged_issue_count(df)
    
    df.to_csv(f'{dir_path}/{stats_name}_err_stats.tsv', sep='\t', index=False)
    df_err_per_file.to_csv(f'{dir_path}/{stats_name}_err_stats_per_file.tsv', sep='\t', index=False)
    df_flagged_issue_count.to_csv(f'{dir_path}/{stats_name}_flagged_issue_count.tsv', sep='\t', index=False)
    print(f'stats saved to {dir_path}/{stats_name}')

# if __name__ == '__main__':
#     SCRIPT_DESCRIPTION = 'Get wellformedness statistics'
#     arg_list = [
#         Argument('-t', '--tsv', str, 'the tsv file'),
#         Argument('-d', '--directory', str, 'the directory containing tsv files'),
#         Argument('-s', '--stats_name', str, 'the name of the tsv stats files (default is stats)'),
#         ]

#     args = generate_argparser_with_arguments(arg_list, script_description=SCRIPT_DESCRIPTION)


#     stats_name = args.stats_name or 'stats'
#     if args.tsv:
#         # print(args.conllx)
#         print(f'Processing {args.tsv}')
#         dir_path = pathlib.Path(args.tsv)
#         df = pd.read_csv(args.tsv, sep='\t')
#         # file_issues = get_flagged_issue_count(df)
#         df.to_csv(f'{dir_path.parent}/{stats_name}_err_stats.tsv', sep='\t')
#         # df_err_per_file.to_csv(f'{dir_path.parent}/{stats_name}_err_stats_per_file.tsv', sep='\t')
#     if args.directory:
#         dir_path = pathlib.Path(args.directory)
#         file_name_list = get_file_names(args.directory, '.tsv')
        
#         df_list = get_df_list(dir_path, file_name_list)
#         save_stats(dir_path, stats_name, df_list)