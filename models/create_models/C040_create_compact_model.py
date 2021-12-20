# Name: Philipp Plamper 
# Date: 20. december 2021

import os
from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_parallel, db_name_compact
from C000_path_variables_create import formula_file_path, transform_file_path, measurement_file_path


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name_parallel = db_name_parallel
db_name_compact = db_name_compact

# path of used files
formula_file_path = formula_file_path # molecule data
transform_file_path = transform_file_path # potential transformations
measurement_file_path = measurement_file_path # measurements


##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name_compact): 
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name_compact)
    print('done: create or replace database')

# establish connection to the new or replaced database based on 'db_name'
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection


# deal with not existing "SAME_AS" relationships
# get all PT relationships
def get_relationships(call_graph):
    new_model_paths = call_graph.run("""
        MATCH (m1:Molecule)-[p:POTENTIAL_TRANSFORMATION]->(m2:Molecule),
            (m1)-[:MEASURED_IN]->(t1:Measurement),
            (m2)-[:MEASURED_IN]->(t2:Measurement)
        OPTIONAL MATCH (m1)-[s1:SAME_AS]->(:Molecule)
        OPTIONAL MATCH (:Molecule)-[s2:SAME_AS]->(m2)
        WHERE t2.point_in_time = t1.point_in_time + 1
        RETURN m1.formula_string as mol_from, m1.peak_relint_tic as mol_from_int, t1.point_in_time as mol_from_time, 
        s1.intensity_trend as mol_from_int_trend, m2.formula_string as mol_to, m2.peak_relint_tic as mol_to_int, 
        t2.point_in_time as mol_to_time, s2.intensity_trend as mol_to_int_trend, p.tu_pt as transformation_unit 
    """).to_data_frame()

    # fill null values of columns matched with 'Optional Match'
    new_model_paths = new_model_paths.fillna(0)


    ### Pfade
    # export
    new_model_paths.to_csv('new_model_transitions/full_paths.csv', sep=',', encoding='utf-8', index=False)




##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
create_database(host, user, passwd, db_name_compact)

# connect to parallel model
call_graph = get_database_connection(host, user, passwd, db_name_parallel)
####



# connect to compact model
call_graph = get_database_connection(host, user, passwd, db_name_parallel)