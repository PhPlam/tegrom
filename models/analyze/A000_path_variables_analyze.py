# Name: Philipp Plamper
# Date: 23. january 2023

import os
import sys

# variables can be imported only if path was added to system
path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) # get system path to variables
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
sys.path.insert(0, path_prefix)

import variables.V001_variables as pv
import variables.V002_functions as pf

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
db_name_light = pv.db_name_light

# query parameters
query_params = pv.model_params

# thresholds
lower_limit = pv.lower_limit
upper_limit = pv.upper_limit

# set filepath prefix for export
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
export_path_prefix = str(abs_path[0]) + '/analyze/analyze_results/' # add path where to save files in project folder
export_path_prefix = export_path_prefix.replace('\\', '/') # necessary for application in Windows
