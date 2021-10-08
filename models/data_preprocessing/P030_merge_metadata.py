# Name: Philipp Plamper
# Date: 08. october 2021

import pandas as pd
from P000_path_variables_preprocess import sample_meta_file, sample_join_file, export_path_metadata


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
    combined_metadata['timepoint'] = timepoint_list
    combined_metadata['time'] = time_list
    combined_metadata['radiation_dose'] = radiation_list
    # drop column description
    extracted_metadata = combined_metadata.drop(['description'], axis=1)
    print('done: extract metadata')
    return extracted_metadata

#export to csv
def export_file(data, export_path):
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    print('done: export data to ' + str(export_path))


##################################################################################
#call functions###################################################################
##################################################################################

# define data
sample_1 = sample_meta_file
sample_2 = sample_join_file

# calculate
combined_metadata = map_ids(sample_1, sample_2)
extracted_metadata = extract_metadata(combined_metadata)

# export to csv
export_file(extracted_metadata, export_path_metadata)
