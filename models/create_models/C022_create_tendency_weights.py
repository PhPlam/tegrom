# Name: Philipp Plamper
# Date: 11. july 2022

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
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# get property intensity_trend from SAME_AS relationship
def get_tendencies(call_graph):
    graph = call_graph
    tendencies = graph.run("""
        MATCH (m:Molecule)
        WITH m.point_in_time as sid, avg(m.peak_relint_tic) as avg_int 
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE m1.point_in_time = sid
        RETURN m1.formula_string AS from_formula, m1.point_in_time AS from_mid, 
                m2.formula_string AS to_formula, m2.point_in_time AS to_mid, 
                s.intensity_trend as intensity_trend, m1.peak_relint_tic as int,
                avg_int
        ORDER BY intensity_trend ASC
    """).to_data_frame()
    print('done: get property intensity_trend')
    return tendencies

# calculate tendency weight for every intensity trend
# inlcudes parts of the calculation of the connected weight
def calc_weights(tendencies, tendency_weight_path):
    MAX = tendencies.intensity_trend.max()
    MIN = tendencies.intensity_trend.min()

    tendency_weight_list = []
    connect_weight_list = []

    for row in tendencies.itertuples():
        if row.intensity_trend >= upper_limit:
            res = row.intensity_trend/MAX # current intensity trend / maximum intensity trend
            tendency_weight_list.append(res)
            connect_weight_list.append(res * (row.int/row.avg_int))
        elif row.intensity_trend <= lower_limit:
            res = (1-row.intensity_trend)/(1-MIN) # (1 - current intensity trend) / (1 - minimum intensity trend)
            tendency_weight_list.append(res)
            connect_weight_list.append(res * (row.int/row.avg_int))
        else:
            tendency_weight_list.append(0)
            connect_weight_list.append(0)

    tendencies['tendency_weight'] = tendency_weight_list
    tendencies['tendency_weight_conn'] = connect_weight_list

    # export calculated weights to csv 
    tendencies.to_csv(tendency_weight_path, sep=',', encoding='utf-8', index=False)

    print('done: calculate tendency weights')
    return tendencies


# add tendency weight property to graph 
# includes adding parts of the later calculated connected weight
def add_weights_to_graph(tendency_weights, call_graph):
    graph = call_graph
    tendency_weights = tendency_weights

    tx = graph.begin()
    for index, row in tendency_weights.iterrows():
        tx.evaluate("""
            MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
            WHERE m1.formula_string = $from_formula AND m1.point_in_time = $from_mid
                AND m2.formula_string = $to_formula AND m2.point_in_time = $to_mid
            SET s.tendency_weight = $tendency_weight
            SET s.tendency_weight_conn = $tendency_weight_conn
        """, parameters= {'from_formula': row['from_formula'], 'from_mid': row['from_mid'], 
        'to_formula': row['to_formula'], 'to_mid': row['to_mid'], 'tendency_weight': row['tendency_weight'], 
        'tendency_weight_conn': row['tendency_weight_conn']})
    graph.commit(tx)

    print('done: add tendency_weight property')

##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = get_database_connection(host, user, passwd, db_name)

# calculate weights and add to graph
tendencies = get_tendencies(call_graph)
tendency_weights = calc_weights(tendencies, tendency_weight_path)
add_weights_to_graph(tendency_weights, call_graph)
