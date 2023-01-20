# Name: Philipp Plamper
# Date: 19. january 2023

import pandas as pd
from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions for calculating weights#########################################
##################################################################################

# get property intensity_trend from SAME_AS relationship
def get_tendencies(session_temporal, query_params):
    tendencies = session_temporal.run(
        "MATCH (m:" + query_params['label_node'] + ") "
        "WITH m." + query_params['prop_node_snapshot'] + " as sid, avg(m." + query_params['prop_node_value'] + ") as avg_int " 
        "MATCH (m1:" + query_params['label_node'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + ") "
        "WHERE m1." + query_params['prop_node_snapshot'] + " = sid "
        "RETURN m1." + query_params['prop_node_name'] + " AS from_formula, "
            "m1." + query_params['prop_node_snapshot'] + " AS from_mid, "
            "m2." + query_params['prop_node_name'] + " AS to_formula, "
            "m2." + query_params['prop_node_snapshot'] + " AS to_mid, "
            "s." + query_params['prop_edge_value_2'] + " as intensity_trend, "
            "m1." + query_params['prop_node_value'] + " as int, "
            "avg_int "
        "ORDER BY intensity_trend ASC"
    ).to_df()
    print('get property ' + query_params['prop_edge_value_2'])
    return tendencies

# calculate tendency weight for every intensity trend
# inlcudes parts of the calculation of the connected weight
def calc_weights(tendencies, upper_limit, lower_limit):
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

    print('calculate tendency weights')
    return tendencies


# add tendency weight property to graph 
# includes adding parts of the later calculated connected weight
def add_weights_to_graph(tendency_weights, session_temporal, query_params):
    for index, row in tendency_weights.iterrows():
        session_temporal.run(
            "MATCH (m1:" + query_params['label_node'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + ") "
            "WHERE m1." + query_params['prop_node_name'] + " = $from_formula AND m1." + query_params['prop_node_snapshot'] + " = $from_mid "
                "AND m2." + query_params['prop_node_name'] + " = $to_formula AND m2." + query_params['prop_node_snapshot'] + " = $to_mid "
            "SET s." + query_params['prop_extra_10'] + " = $tendency_weight "
            "SET s." + query_params['prop_extra_11'] + " = $tendency_weight_conn"
        , parameters= {'from_formula': row['from_formula'], 
            'from_mid': row['from_mid'], 
            'to_formula': row['to_formula'], 
            'to_mid': row['to_mid'], 
            'tendency_weight': row['tendency_weight'], 
            'tendency_weight_conn': row['tendency_weight_conn']})

    print('add tendency_weight property')

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # establish connection to graph
    session_temporal = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # calculate weights and add to graph
    tendencies = get_tendencies(session_temporal, pvc.query_params)
    tendency_weights = calc_weights(tendencies, pvc.upper_limit, pvc.lower_limit)
    add_weights_to_graph(tendency_weights, session_temporal, pvc.query_params)

    # close session
    session_temporal.close()