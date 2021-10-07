# Name: Philipp Plamper
# Date: 07. october 2021

import pandas as pd
from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_parallel
from C000_path_variables_create import lower_limit, upper_limit
from C000_path_variables_create import tendency_weight_path

# pd.options.mode.chained_assignment = None

##################################################################################
#settings#########################################################################
##################################################################################

# credentials  
host = host
user = user
passwd = passwd

# select database
db_name = db_name_parallel

# path of used files
tendency_weight_path = tendency_weight_path # calculated weights

# fault tolerance for intensity trend 
lower_limit = lower_limit
upper_limit = upper_limit

##################################################################################
#define functions for calculating weights#########################################
##################################################################################

# establish connection to the database
def get_database_connection():
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# get property intensity_trend from SAME_AS relationship
def get_tendencies(call_graph):
    graph = call_graph
    tendencies = graph.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        RETURN m1.formula_string AS from_formula, m1.sample_id AS from_mid, m2.formula_string AS to_formula, m2.sample_id AS to_mid, s.intensity_trend as intensity_trend, m1.peak_relint_tic as int
        ORDER BY intensity_trend ASC
    """).to_data_frame()
    print('done: get property intensity_trend')
    return tendencies

# calculate tendency weight for every intensity trend
# inlcudes parts of the calculation of the connected weight
def calc_weights(tendencies):
    MAX = tendencies.intensity_trend.max()
    MIN = tendencies.intensity_trend.min()

    tendency_weight_list = []
    connect_weight_list = []

    for row in tendencies.itertuples():
        if row.intensity_trend >= upper_limit:
            res = row.intensity_trend/MAX # current intensity trend / maximum intensity trend
            tendency_weight_list.append(res)
            connect_weight_list.append(res * row.int)
        elif row.intensity_trend <= lower_limit:
            res = (1-row.intensity_trend)/(1-MIN) # (1 - current intensity trend) / (1 - minimum intensity trend)
            tendency_weight_list.append(res)
            connect_weight_list.append(res * row.int)
        else:
            tendency_weight_list.append(0) 
            connect_weight_list.append(0)

    tendencies['tendency_weight'] = tendency_weight_list
    tendencies['tendency_weight_conn'] = connect_weight_list

    # export calculated weights to csv 
    tendencies.to_csv(tendency_weight_path, sep=',', encoding='utf-8', index=False)
    print('done: calculate and save tendency weights')

# add tendency weight property to graph 
# includes adding parts of the later calculated connected weight
def add_weights_to_graph(tendency_weight_path, call_graph):
    graph = call_graph
    graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + tendency_weight_path + """' AS row
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE m1.formula_string = row.from_formula AND m1.sample_id = row.from_mid
	    AND m2.formula_string = row.to_formula AND m2.sample_id = row.to_mid
        SET s.tendency_weight = row.tendency_weight
        SET s.tendency_weight_conn = row.tendency_weight_conn
    """)
    print('done: add tendency_weight property')

##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = get_database_connection()

# calculate weights and add to graph
tendencies = get_tendencies(call_graph)
calculate_tendency_weights = calc_weights(tendencies)
add_weights_to_graph(tendency_weight_path, call_graph)
