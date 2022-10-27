# Name: Philipp Plamper
# Date: 27. october 2022

# contains path variables used to create models
# contains test functions to check reliabilty of data

import pandas as pd
import os
import sys
from py2neo import Graph

abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) # add path to files in project folder
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
db_name_rev = pv.db_name_rev

# query parameters
query_params = pv.model_params

folder = '/files_for_model/'

written_transformations_file_path = path_prefix + folder + pv.file_transformation_units # path to transformation units
# files created in preprocessing
formula_file_path = path_prefix + folder + pv.cleaned_molecules # path to dataset with molecule data
transform_file_path = path_prefix + folder + pv.relationships # path to calculated potential transformations
measurement_file_path = path_prefix + folder + pv.metadata # path to measurements
unique_formulas_file_path = path_prefix + folder + pv.unique_molecules # path to unique formulas

# define fault tolerance for intensity trend 
upper_limit = pv.upper_limit # above considered as increasing intensity
lower_limit = pv.lower_limit # below considered as decreasing intensity


##################################################################################
# function to create and to connect to database ##################################
##################################################################################

# establish connection to the new or replaced database based on 'db_name'
def connect_to_database(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name): 
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name)
    print('done: create or replace database')