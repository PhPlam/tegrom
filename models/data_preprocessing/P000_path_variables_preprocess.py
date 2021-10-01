# Name: Philipp Plamper
# Date: 11. may 2021

# contains path variables used by data preprocessing scripts
# contains test functions to check reliabilty of data

import pandas as pd
import os


##################################################################################
#set variables for data preprocessing scritps#####################################
##################################################################################

# set relative filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get path to files
path_prefix = str(abs_path[0]) + '/files_for_model/' # absolute path to used files
path_prefix = path_prefix.replace('\\', '/') 

#remove duplicates molecule#######################################################

# load raw data
try:
    load_file = 'ufz_all_formulas_raw.csv'
    raw_file_path = path_prefix + load_file
    raw_data = pd.read_csv(raw_file_path, sep=';')
except FileNotFoundError:
    pass

# path to export csv (preprocess)
try:
    result_file_preprocess = 'unique_formula_strings.csv'
    export_path_preprocess = path_prefix + result_file_preprocess
except FileNotFoundError:
    pass

# path to export cleaned csv (preprocess)
try:
    result_file_cleaning = 'ufz_all_formulas_cleaned.csv'
    cleaned_file_path = path_prefix + result_file_cleaning
except FileNotFoundError:
    pass


#create transform relationship####################################################

# load unique formulas (result from "remove duplicate molecule")
try:
    formulas_file = 'unique_formula_strings.csv'
    formulas_path = path_prefix + formulas_file
    formula_strings = pd.read_csv(formulas_path)
except FileNotFoundError:
    pass

# load transformation unit
try:
    transformation_unit_file = 'transformations_handwritten.csv'
    groups_path = path_prefix + transformation_unit_file
    transformation_unit = pd.read_csv(groups_path)
except FileNotFoundError:
    pass

# path to export csv (create)
try:
    result_file_create = 'formula_relationships.csv'
    export_path_create = path_prefix + result_file_create
except FileNotFoundError:
    pass


#prepare metadata#################################################################

# metadata 
try: 
    sample_meta_name = 'ufz_sample_meta_raw.csv'
    sample_meta_path = path_prefix + sample_meta_name
    sample_meta_file = pd.read_csv(sample_meta_path, sep=';')
except FileNotFoundError:
    pass


# join table for measurement_ids
try:
    sample_join_name = 'ufz_sample_join_raw.csv'
    sample_join_path = path_prefix + sample_join_name
    sample_join_file = pd.read_csv(sample_join_path, sep=';')
except FileExistsError:
    pass

# path to export csv
try: 
    meta_file_create = 'sample_metadata.csv'
    export_path_metadata = path_prefix + meta_file_create
except FileNotFoundError:
    pass


##################################################################################
#test functions for unittests#####################################################
##################################################################################

def testPhoto():
    return list(raw_data)

def testUnique():
    return list(formula_strings)

def testFunctional():
    return list(transformation_unit)

def testMeta():
    return list(sample_meta_file)

def testJoin():
    return list(sample_join_file)