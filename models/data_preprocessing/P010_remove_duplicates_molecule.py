# Name: Philipp Plamper
# Date: 19. january 2021

import pandas as pd
from P000_path_variables_preprocess import raw_data, export_path_preprocess, raw_file_path, cleaned_file_path


##################################################################################
#preprocess data##################################################################
##################################################################################

# get data path 
data = raw_data

# overwrite raw_data to fill null values with 0
data_rm_null = data
data_rm_null = data_rm_null.fillna(0)
data_rm_null['C'] = data_rm_null['C'].astype('Int64')
data_rm_null['H'] = data_rm_null['H'].astype('Int64')
data_rm_null['O'] = data_rm_null['O'].astype('Int64')
data_rm_null['N'] = data_rm_null['N'].astype('Int64')
data_rm_null['S'] = data_rm_null['S'].astype('Int64')

# select columns
data = data[['measurement_id', 'formula_string', 'formula_class', 'C', 'H', 'O', 'N', 'S']]
# fill nan with zeros and change from float to integer
data = data.fillna(0)
data['C'] = data['C'].astype('Int64')
data['H'] = data['H'].astype('Int64')
data['O'] = data['O'].astype('Int64')
data['N'] = data['N'].astype('Int64')
data['S'] = data['S'].astype('Int64')

# remove duplicates
data = data.drop_duplicates(subset=['formula_string'])


##################################################################################
#export data######################################################################
##################################################################################

# export unique formula strings
export_path = export_path_preprocess
data.to_csv(export_path, sep=',', encoding='utf-8', index=False)

# export cleaned raw formulas with filled null values
data_clean = data_rm_null
data_clean.to_csv(cleaned_file_path, sep=',', encoding='utf-8', index=False)

##################################################################################
##################################################################################
##################################################################################
