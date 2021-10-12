# Name: Philipp Plamper
# Date: 12. october 2021

# contains path variables used to analyze models

import os


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

# set filepath prefix for export
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/analyze/analyze_results/' # add path where to save files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

# filepath prefix for existing files
path_prefix_csv = str(abs_path[0]) + '/files_for_model/' # add path to files in project folder
path_prefix_csv = path_prefix_csv.replace('\\', '/') # necessary for application in Windows
