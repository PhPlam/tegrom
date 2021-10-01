# Name: Philipp Plamper
# Date: 14. december 2020

import pandas as pd

from P000_path_variables_preprocess import sample_meta_file, sample_join_file, export_path_metadata

##################################################################################
#merge metadata information#######################################################
##################################################################################

# load data and join on sample_id
sample_1 = sample_meta_file
sample_2 = sample_join_file
metadata = sample_2.merge(sample_1, on='sample_id')
metadata = metadata[['sample_id', 'measurement_id', 'description']]
metadata['description'] = metadata.description.str.split(',')

# split description to separate values
timepoint_list = []
time_list = []
radiation_list = []
for row in metadata.itertuples():
    timepoint_list.append(row.description[0].strip('timepoint ='))
    time_list.append(row.description[1].strip('time ='))
    radiation_list.append(row.description[2].strip('radiation_dose ='))

metadata['timepoint'] = timepoint_list
metadata['time'] = time_list
metadata['radiation_dose'] = radiation_list

# drop column description
metadata = metadata.drop(['description'], axis=1)


# export to csv
export_path = export_path_metadata
metadata.to_csv(export_path, sep=',', encoding='utf-8', index=False, float_format='%.f')


