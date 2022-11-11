# Name: Philipp Plamper
# Date: 08. november 2022

import os
import sys

# variables can be imported only if path was added to system
path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) # get system path to variables
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
sys.path.insert(0, path_prefix)

import variables.V001_variables as pv

##################################################################################
#set variables for models#########################################################
##################################################################################

# host + port
host = pv.host

# credentials for API
user = pv.user
passwd = pv.passwd

# select database
db_name_temporal = pv.db_name_temporal
db_name_smash = pv.db_name_smash

# query parameters
query_params = pv.model_params

# thresholds
lower_limit = pv.lower_limit
upper_limit = pv.upper_limit

# set filepath prefix for export
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/analyze/analyze_results/' # add path where to save files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

# filepath prefix for existing files
path_prefix_csv = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
path_prefix_csv = path_prefix_csv.replace('\\', '/') # necessary for application in Windows

# select transformation units for visualization of development over time
# select the same for single visualization
tu = 'H2 O1'
tu_2 = '-H2 -O1'
