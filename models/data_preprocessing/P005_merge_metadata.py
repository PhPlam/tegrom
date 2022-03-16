# Name: Philipp Plamper
# Date: 16. march 2022

import pandas as pd
from P000_path_variables_preprocess import sample_meta_file_csv, sample_join_file_csv 
from P000_path_variables_preprocess import export_path_metadata


##################################################################################
#map Ids and get metadata#########################################################
##################################################################################

# merge data on sample_id
def map_ids(sample_1, sample_2):
    metadata = sample_2.merge(sample_1, on='sample_id')
    metadata = metadata[['sample_id', 'measurement_id', 'description']]
    print('done: map IDs')
    return metadata

# extract parts from metadata
def extract_metadata(combined_metadata):
    combined_metadata['description'] = combined_metadata.description.str.split(',')
    # split description to separate values
    timepoint_list = []
    time_list = []
    radiation_list = []
    for row in combined_metadata.itertuples():
        timepoint_list.append(row.description[0].strip('timepoint ='))
        time_list.append(row.description[1].strip('time ='))
        radiation_list.append(row.description[2].strip('radiation_dose ='))
    timepoint_list = [int(x) for x in timepoint_list]
    combined_metadata['timepoint'] = timepoint_list
    combined_metadata['time'] = time_list
    combined_metadata['radiation_dose'] = radiation_list
    # drop column description
    extracted_metadata = combined_metadata.drop(['description'], axis=1)
    print('done: extract metadata')
    return extracted_metadata

# remove measurements from data
def remove_measurements(extracted_data, time_list):
    time_list = []
    for point_in_time in time_list:
        extracted_data = extracted_data[extracted_data.timepoint != point_in_time]

    n = 0   
    for index, row in extracted_data.iterrows():
        extracted_data.at[index,'timepoint'] = n
        n += 1
   
    removed_measurements = extracted_data.reset_index(drop=True)
    print('done: remove measurements')
    return removed_measurements

#export to csv
def export_file(data, export_path):
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    print('done: export data to ' + str(export_path))


##################################################################################
#call functions###################################################################
##################################################################################

# define data
sample_1 = sample_meta_file_csv
sample_2 = sample_join_file_csv
time_list = []

# calculate
combined_metadata = map_ids(sample_1, sample_2)
extracted_metadata = extract_metadata(combined_metadata)
removed_measurements = remove_measurements(extracted_metadata, time_list)

# export to csv
export_file(removed_measurements, export_path_metadata)
