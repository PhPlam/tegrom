# Name: Philipp Plamper
# Date: 25. october 2022

# functions to load and export csv files for preprocessing

import pandas as pd
import os

##################################################################################
# functions to load and export data ##############################################
##################################################################################

# set path for data preprocessing scripts
def get_path_prefix():
    
    # set relative filepath prefix
    abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
    path_prefix = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
    path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

    return path_prefix

# load csv files
def load_csv(filename, seperator):

    path_prefix = get_path_prefix()
    try:
        load_file = filename
        raw_file_path = path_prefix + load_file
        raw_data_csv = pd.read_csv(raw_file_path, sep=seperator)
        return raw_data_csv

    except FileNotFoundError:
        print('info: cannot load file ' + filename)
        pass

#export data to csv
def export_csv(filename, data):
    
    path_prefix = get_path_prefix()
    filename_result = filename
    export_path = path_prefix + filename_result
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    
    print('done: export data to ' + str(export_path))
