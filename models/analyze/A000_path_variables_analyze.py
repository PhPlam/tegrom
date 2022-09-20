# Name: Philipp Plamper
# Date: 20. september 2022

# contains path variables used to analyze models

import os
import A001_parameters_analysis as pa

##################################################################################
#set variables for models#########################################################
##################################################################################

# host + port
host = pa.host

# credentials for API
user = pa.user
passwd = pa.passwd

# select database
db_name_temporal = pa.db_name_temporal
db_name_smash = pa.db_name_smash

# set filepath prefix for export
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/analyze/analyze_results/' # add path where to save files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

# filepath prefix for existing files
path_prefix_csv = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
path_prefix_csv = path_prefix_csv.replace('\\', '/') # necessary for application in Windows
