# Name: Philipp Plamper
# Date: 08. october 2021

import pandas as pd
from P000_path_variables_preprocess import raw_data, export_path_preprocess, cleaned_file_path


##################################################################################
#clean data by removing null values###############################################
##################################################################################

# fill null values with 0
def fill_null_values(original_data):
    data_rm_null = original_data
    data_rm_null = data_rm_null.fillna(0)
    data_rm_null['C'] = data_rm_null['C'].astype('Int64')
    data_rm_null['H'] = data_rm_null['H'].astype('Int64')
    data_rm_null['O'] = data_rm_null['O'].astype('Int64')
    data_rm_null['N'] = data_rm_null['N'].astype('Int64')
    data_rm_null['S'] = data_rm_null['S'].astype('Int64')
    print('done: fill null values with 0')
    return data_rm_null

# remove duplicate formula strings
def delete_duplicates(filled_data):
    data = filled_data[['measurement_id', 'formula_string', 'formula_class', 'C', 'H', 'O', 'N', 'S']]
    data = data.drop_duplicates(subset=['formula_string'])
    print('done: remove duplicate formula strings')
    return data

# export to csv
def export_file(data, export_path):
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    print('done: export data to ' + str(export_path))


##################################################################################
#call functions###################################################################
##################################################################################

# define data
original_data = raw_data

#calculate 
filled_data = fill_null_values(original_data)
removed_duplicate_data = delete_duplicates(filled_data)

# export to csv
export_file(filled_data, cleaned_file_path)
export_file(removed_duplicate_data, export_path_preprocess)
