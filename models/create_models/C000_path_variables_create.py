# Name: Philipp Plamper
# Date: 15. december 2020

# contains path variables used by create models scripts
# contains test functions to check reliabilty of data

import pandas as pd
import os
from py2neo import Graph


##################################################################################
#set variables for create models scritps##########################################
##################################################################################

# host + port
host = 'http://localhost:7474'

# credentials for API
user = 'neo4j'
passwd = '1234'

# select db
db_name_compact = 'modelcompact'
db_name_parallel = 'modelparalleltest'

# set relative filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get path to files
path_prefix = str(abs_path[0]) + '/files_for_model/' # absolute path to used files
path_prefix = path_prefix.replace('\\', '/')

# use filenames if files are stored in import folder of neo4j instance, remove 'path_prefix'
formula_file_path = path_prefix + 'ufz_all_formulas_cleaned.csv' # path to dataset with molecule data
transform_file_path = path_prefix + 'formula_relationships.csv' # path to CAN_TRANSFORM_INTO relationships
measurement_file_path = path_prefix + 'sample_metadata.csv' # path to measurements
unique_formulas_file_path = path_prefix + 'unique_formula_strings.csv' # path to strings with unique formulas
written_transformations_file_path = path_prefix + 'transformations_handwritten.csv'

# filename for increasing intensity csv
int_change_path = path_prefix + 'increasing_intensities.csv'

# fault tolerance MS
# considered as increasing intensity
upper_limit = 1.025
# considered as decreasing intensity
lower_limit = 0.975

#filename for weights
tendency_weight_path = path_prefix + 'tendency_weights.csv'


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
