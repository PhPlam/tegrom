# Name: Philipp Plamper
# Date: 23. june 2022

# contains path variables used to create models
# contains test functions to check reliabilty of data

import pandas as pd
import os
from py2neo import Graph
import C001_parameters_temporal_graph as ptg


##################################################################################
#set variables for models#########################################################
##################################################################################

# host + port
host = ptg.host

# credentials for API
user = ptg.user
passwd = ptg.passwd

# select database
db_name_temporal = ptg.db_name_temporal
db_name_smash = ptg.db_name_smash

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
upper_limit = ptg.upper_limit # above considered as increasing intensity
lower_limit = ptg.lower_limit # below considered as decreasing intensity
