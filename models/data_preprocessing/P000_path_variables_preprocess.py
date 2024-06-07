# Name: Philipp Plamper
# Date: 07. june 2024

import pandas as pd
import os
import sys

# variables can be imported only if path was added to system
path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) # get system path to variables
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
sys.path.insert(0, path_prefix)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../variables')))

import variables.V001_variables as pv

##################################################################################
# paths and files ################################################################
##################################################################################

# see module for description of paths
file_molecules = pv.file_molecules
file_transformation_units = pv.file_transformation_units
file_sample_meta = pv.file_sample_meta
file_sample_join = pv.file_sample_join
unique_molecules = pv.unique_molecules
cleaned_molecules = pv.cleaned_molecules
relationships = pv.relationships
metadata = pv.metadata
photolysis = pv.photolysis

##################################################################################
# functions to load and export data ##############################################
##################################################################################

# set path for data preprocessing scripts
def get_path_prefix():
    
    # set relative path to files for import and export
    file_path = '/files_for_model/'
    path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) + file_path
    path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

    return path_prefix

# load csv files
def load_csv(filename, seperator):

    path_prefix = get_path_prefix()
    try:
        load_file = filename
        raw_file_path = path_prefix + load_file
        try:
            raw_data_csv = pd.read_csv(raw_file_path, sep=seperator[0])
        except Exception:
            raw_data_csv = pd.read_csv(raw_file_path, sep=seperator[1])

        return raw_data_csv

    except FileNotFoundError:
        print('info: cannot load file ' + filename)
        pass

# export data to csv
def export_csv(filename, data):
    
    path_prefix = get_path_prefix()
    filename_result = filename
    export_path = path_prefix + filename_result
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    
    print('done: export data to ' + str(export_path))
