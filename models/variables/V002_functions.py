# Name: Philipp Plamper 
# Date: 23. january 2023

import os
from neo4j import GraphDatabase

# variables can be imported only if path was added to system
#path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) # get system path to variables
#path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows
#sys.path.insert(0, path_prefix)

#import variables.V001_variables as var

### functions to ###
### provide functionality ###

# establish connection to the new or replaced database based on 'db_name'
def connect_to_database(host, user, passwd, db_name):
    # credentials
    URI = host
    AUTH = (user, passwd)
    DB = db_name
    # create connection and open session
    driver = GraphDatabase.driver(URI, auth=AUTH, database=DB)
    session = driver.session()
    print('establish connection to database: ' + db_name)
    return session

# set path for data preprocessing scripts
def get_path_prefix(path_to_folder):
    
    # set relative path to files for import and export
    file_path = path_to_folder
    path_prefix = str(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]) + file_path
    path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows

    return path_prefix

# load csv files
def load_csv(filename, seperator):

    path_prefix = get_path_prefix()
    try:
        load_file = filename
        raw_file_path = path_prefix + load_file
        raw_data_csv = pd.read_csv(raw_file_path, sep=seperator)
        return raw_data_csv

    except FileNotFoundError:
        print('info: cannot load file ' + filename)
        pass

# export data to csv
def export_csv(filename, data):
    
    path_prefix = get_path_prefix()
    filename_result = filename
    export_path = path_prefix + filename_result
    data.to_csv(export_path, sep=',', encoding='utf-8', index=False)
    
    print('done: export data to ' + str(export_path))


### functions for ###
### graph analysis ###

def graph_get_time(session, query_params):
    df_time = session.run(
        "MATCH (m:" + query_params['label_node'] + ") "
        "RETURN count(m) as count_nodes, "
            "m." + query_params['prop_node_snapshot'] + " as property_time, "
            "m." + query_params['prop_extra_12'] + " as radiation_dose "
        "ORDER BY property_time ASC"
    ).to_df()

    print('done: get all time sequences')
    return df_time

def graph_get_member_intensity_trend(session, query_params, lower, upper, trend):
    df_member_trend = session.run(
        "MATCH (m:" + query_params['label_node'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + ") "
        "WHERE " + str(lower) + " <= s." + query_params['prop_edge_value_2'] + " <= " + str(upper) + " "
        "RETURN m." + query_params['prop_node_snapshot'] + "+1 as property_time, "
            "count(s) as " + trend + " "
        "ORDER BY property_time ASC"
    ).to_df()

    print('done: get member of trend: ' + trend)
    return df_member_trend

def graph_get_transformations(session, edge_type, query_params):
    df_transformations = session.run(
        "MATCH (m1:" + query_params['label_node'] + ")-[c:" + edge_type + "]->(m2:" + query_params['label_node'] + ") "
        "RETURN m1." + query_params['prop_node_snapshot'] + "+1 as property_time, "
            "count(c) as count_relationships"
    ).to_df()

    print('done: get transformations: ' + edge_type)
    return df_transformations