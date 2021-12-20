# Name: Philipp Plamper
# Date: 20. december 2021

# contains path variables used to create models
# contains test functions to check reliabilty of data

import pandas as pd
import os
from py2neo import Graph


##################################################################################
#set variables for models#########################################################
##################################################################################

# host + port
host = 'http://localhost:7474'

# credentials for API
user = 'neo4j'
passwd = '1234'

# select database
db_name_parallel = 'modelparallel'
db_name_compact = 'modelcompact'

# set filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

# define path to files
# given files
written_transformations_file_path = path_prefix + 'transformations_handwritten.csv' # path to transformation units
# files created in preprocessing
formula_file_path = path_prefix + 'ufz_all_formulas_cleaned.csv' # path to dataset with molecule data
transform_file_path = path_prefix + 'formula_relationships.csv' # path to calculated potential transformations
measurement_file_path = path_prefix + 'sample_metadata.csv' # path to measurements
unique_formulas_file_path = path_prefix + 'unique_formula_strings.csv' # path to unique formulas
# files created in runtime
int_change_path = path_prefix + 'increasing_intensities.csv' # path to calculated occurring transformations (RelIdent-Algorithm)
tendency_weight_path = path_prefix + 'tendency_weights.csv' # path to calculated weights

# define fault tolerance for intensity trend 
upper_limit = 1.025 # above considered as increasing intensity
lower_limit = 0.975 # below considered as decreasing intensity


##################################################################################
#test functions for unittests#####################################################
##################################################################################

def testSample():
    measurement_file = pd.read_csv(measurement_file_path, nrows=5)
    return list(measurement_file)

def testRelationships():
    transform_file = pd.read_csv(transform_file_path, nrows=5)
    return list(transform_file)

def testIntensityCSV():
    int_change_file = pd.read_csv(int_change_path, nrows=5)
    return list(int_change_file)

def testWeightCSV():
    tendency_weight_file = pd.read_csv(tendency_weight_path, nrows=5)
    return list(tendency_weight_file)

def testDbConnection():
    connect_db = Graph(host, auth=(user, passwd), name='system')
    connect_db.run("")
    return "works"
