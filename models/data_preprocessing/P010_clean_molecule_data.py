# Name: Philipp Plamper
# Date: 26. october 2022

import pandas as pd
import P001_parameters_preprocessing as pp
import P000_path_variables_preprocess as pvp


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

# remove molecules with specific atom count greater than ...
def remove_molecules(filled_data):
    filled_data = filled_data[filled_data.C <= 999]
    filled_data = filled_data[filled_data.H <= 999]
    filled_data = filled_data[filled_data.O <= 999]
    filled_data = filled_data[filled_data.N <= 2]
    shrinked_data = filled_data[filled_data.S <= 1]
    print('done: remove molecules with specific atom count')
    return shrinked_data

# remove molecules from removed measurements
def remove_molecules_without_measurement(shrinked_data, metadata):
    measurement_list = metadata['measurement_id'].to_list()
    removed_molecules_without_measurement = shrinked_data[shrinked_data.measurement_id.isin(measurement_list)]
    removed_molecules_without_measurement = removed_molecules_without_measurement.reset_index(drop=True)
    removed_molecules_without_measurement = removed_molecules_without_measurement.merge(metadata,how='inner',left_on=['measurement_id'],right_on=['measurement_id'])
    print('done: remove molecules without measurements')
    return removed_molecules_without_measurement

# remove duplicate formula strings
def delete_duplicates(removed_molecules_without_measurement):
    data = removed_molecules_without_measurement[['measurement_id', 'formula_string', 'formula_class', 'C', 'H', 'O', 'N', 'S']]
    data = data.drop_duplicates(subset=['formula_string'])
    print('done: remove duplicate formula strings')
    return data


##################################################################################
#call functions###################################################################
##################################################################################

# define data
original_data = pvp.load_csv(pp.file_molecules, seperator=';')
metadata = pvp.load_csv(pp.metadata, seperator=',')

#calculate 
filled_data = fill_null_values(original_data)
shrinked_data = remove_molecules(filled_data)
removed_molecules_without_measurement = remove_molecules_without_measurement(shrinked_data, metadata)
removed_duplicate_data = delete_duplicates(removed_molecules_without_measurement)

# export to csv
pvp.export_csv(pp.cleaned_molecules, removed_molecules_without_measurement)
pvp.export_csv(pp.unique_molecules, removed_duplicate_data)
