# Name: Philipp Plamper
# Date: 06. march 2023

import pandas as pd
import P000_path_variables_preprocess as pvp


##################################################################################
#clean data by removing null values###############################################
##################################################################################

# keep only necessary columns
def remove_unused_columns(original_data):
    df_removed_columns = original_data[['measurement_id', 'peak_relint_tic', 'formula_string', 'C', 'H', 'N', 'O', 'S', 'formula_mass_nominal']]
    print('done: remove unused columns')
    return df_removed_columns

# get timepoints from "measurement_ids"
def create_time_order(data):
    data = data.copy()
    i = 0
    for ele in data['measurement_id'].unique():
        data.loc[data.measurement_id == ele, 'timepoint'] = i
        i+=1

    data['timepoint'] = data['timepoint'].astype('int')

    print('done: create column with snapshots')
    return data

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
# deprecated ???
def remove_molecules_without_measurement(shrinked_data, metadata):
    measurement_list = metadata['measurement_id'].to_list()
    removed_molecules_without_measurement = shrinked_data[shrinked_data.measurement_id.isin(measurement_list)]
    removed_molecules_without_measurement = removed_molecules_without_measurement.reset_index(drop=True)
    removed_molecules_without_measurement = removed_molecules_without_measurement.merge(metadata,how='inner',left_on=['measurement_id'],right_on=['measurement_id'])
    print('done: remove molecules without measurements')
    return removed_molecules_without_measurement

# remove duplicate formula strings
def delete_duplicates(removed_molecules_without_measurement):
    data = removed_molecules_without_measurement[['measurement_id', 'formula_string', 'C', 'H', 'O', 'N', 'S']]
    data = data.drop_duplicates(subset=['formula_string'])
    print('done: remove duplicate formula strings')
    return data

# create pipeline for better overview in sequential function calls
def pipeline(data, *filters):
    for filter in filters:
        data = filter(data)
    return data 


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':

    # define data
    original_data = pvp.load_csv(pvp.file_molecules, seperator=';')
    metadata = pvp.load_csv(pvp.metadata, seperator=',')

    # clean molecule data
    data_all_molecules = pipeline(original_data,
                                remove_unused_columns,
                                create_time_order,
                                fill_null_values,
                                remove_molecules)

    data_unique_molecules = pipeline(original_data,
                                remove_unused_columns,
                                create_time_order,
                                fill_null_values,
                                remove_molecules,
                                delete_duplicates)

    # export to csv
    pvp.export_csv(pvp.cleaned_molecules, data_all_molecules)
    pvp.export_csv(pvp.unique_molecules, data_unique_molecules)
