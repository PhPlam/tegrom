# Name: Philipp Plamper
# Date: 08. october 2021

# contains path variables used by data preprocessing scripts
# contains test functions to check reliabilty of data

import pandas as pd
import os


##################################################################################
#set path for data preprocessing scripts##########################################
##################################################################################

# set relative filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows


##################################################################################
#files for step: fill null values and remove duplicates ##########################
##################################################################################

# get raw file with all molecules
try:
    load_file = 'ufz_all_formulas_raw.csv'
    raw_file_path = path_prefix + load_file
    raw_data_csv = pd.read_csv(raw_file_path, sep=';')
except FileNotFoundError:
    print('info: cannot load file with raw molecule data')
    pass

# path to export csv with unique formula strings
try:
    result_file_preprocess = 'unique_formula_strings.csv'
    export_path_preprocess = path_prefix + result_file_preprocess
except FileNotFoundError:
    print('info: no file with unique formula strings found')
    pass

# path to export csv with filled null values
try:
    result_file_cleaning = 'ufz_all_formulas_cleaned.csv'
    cleaned_file_path = path_prefix + result_file_cleaning
except FileNotFoundError:
    print('info: no file with cleaned molecule data found')
    pass


##################################################################################
#files for step: calculate possible transformations###############################
##################################################################################

# load file with unique formulas
try:
    formulas_file = 'unique_formula_strings.csv'
    formulas_path = path_prefix + formulas_file
    formula_strings_csv = pd.read_csv(formulas_path)
except FileNotFoundError:
    print('info: cannot load file with unique formula strings')
    pass

# load file with transformation units
try:
    transformation_unit_file = 'transformations_handwritten.csv'
    groups_path = path_prefix + transformation_unit_file
    transformation_unit_csv = pd.read_csv(groups_path)
except FileNotFoundError:
    print('info: cannot load file with transformation units')
    pass

# path to export csv (create)
try:
    result_file_create = 'formula_relationships.csv'
    export_path_create = path_prefix + result_file_create
except FileNotFoundError:
    print('info: no file with possible transformations found')
    pass


##################################################################################
#files for step: map IDs and metadata#############################################
##################################################################################

# load file with metadata of measurements
try: 
    sample_meta_name = 'ufz_sample_meta_raw.csv'
    sample_meta_path = path_prefix + sample_meta_name
    sample_meta_file_csv = pd.read_csv(sample_meta_path, sep=';')
except FileNotFoundError:
    print('info: cannot load file with metadata')
    pass


# load file with ID mapping
try:
    sample_join_name = 'ufz_sample_join_raw.csv'
    sample_join_path = path_prefix + sample_join_name
    sample_join_file_csv = pd.read_csv(sample_join_path, sep=';')
except FileExistsError:
    print('info: cannot load file with ID mapping')
    pass

# path to export csv
try: 
    meta_file_create = 'sample_metadata.csv'
    export_path_metadata = path_prefix + meta_file_create
except FileNotFoundError:
    print('print: no file with mapped IDs and metadata found')
    pass

# load file with metadata
try:
    meta_file_name = 'sample_metadata.csv'
    meta_file_path = path_prefix + meta_file_name
    meta_file_file_csv = pd.read_csv(meta_file_path, sep=',')
except FileExistsError:
    print('info: cannot load file with metadata')
    pass


##################################################################################
#test functions for unittests#####################################################
##################################################################################

def testPhoto():
    return list(raw_data_csv)

def testUnique():
    return list(formula_strings_csv)

def testFunctional():
    return list(transformation_unit_csv)

def testMeta():
    return list(sample_meta_file_csv)

def testJoin():
    return list(sample_join_file_csv)