# Name: Philipp Plamper
# Date: 17. january 2023

import pandas as pd
import os
import sys
from neo4j import GraphDatabase

# variables can be imported only if path was added to system
path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) # get system path to variables
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
sys.path.insert(0, path_prefix)

import variables.V001_variables as pv
import variables.V002_functions as pf

##################################################################################
#set variables for models#########################################################
## see module for further description ############################################
##################################################################################

# host + port
host = pv.host

# credentials for API
user = pv.user
passwd = pv.passwd

# select database
db_name_temporal = pv.db_name_temporal
db_name_light = pv.db_name_light
#db_name_rev = pv.db_name_rev

# query parameters
query_params = pv.model_params

# paths
folder = '/files_for_model/'
written_transformations_file_path = path_prefix + folder + pv.file_transformation_units
formula_file_path = path_prefix + folder + pv.cleaned_molecules
transform_file_path = path_prefix + folder + pv.relationships 
measurement_file_path = path_prefix + folder + pv.metadata
unique_formulas_file_path = path_prefix + folder + pv.unique_molecules

# threshold
upper_limit = pv.upper_limit
lower_limit = pv.lower_limit


##################################################################################
# function to create and to connect to database ##################################
##################################################################################

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name): 
    # connect to systemdb and create database 
    systemdb = 'system'
    session = pf.connect_to_database(host, user, passwd, systemdb)
    session.run("CREATE OR REPLACE DATABASE " + db_name)
    # close session
    session.close()
    print('done: create or replace database ' + db_name)