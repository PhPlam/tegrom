# Name: Philipp Plamper
# Date: 12. october 2021

# contains path variables used to analyze models

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

# set filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/analyze/analyze_results/' # add path to files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
