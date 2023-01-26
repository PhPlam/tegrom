# Name: Philipp Plamper
# Date: 26. january 2023

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
    print('done: get property ' + query_params['prop_edge_value_2'])
    return tendencies

# calculate tendency weight for every intensity trend (intermediate weight)
def calc_weights(tendencies, upper_limit, lower_limit):
    MAX = tendencies.intensity_trend.max()
    MIN = tendencies.intensity_trend.min()

    weight_list = []

    for row in tendencies.itertuples():
        if row.intensity_trend >= upper_limit:
            res = row.intensity_trend/MAX # current intensity trend / maximum intensity trend
            weight_list.append(res * (row.int/row.avg_int))
        elif row.intensity_trend <= lower_limit:
            res = (1-row.intensity_trend)/(1-MIN) # (1 - current intensity trend) / (1 - minimum intensity trend)
            weight_list.append(res * (row.int/row.avg_int))
        else:
            weight_list.append(0)

    tendencies['tendency_weight'] = weight_list

    print('done: calculate edge weight')
    return tendencies


# add tendency weight property to edges
def calc_temp_weights(tendency_weights, session_temporal, query_params):
    for index, row in tendency_weights.iterrows():
        session_temporal.run(
            "MATCH (m1:" + query_params['label_node'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + ") "
            "WHERE m1." + query_params['prop_node_name'] + " = $from_formula AND m1." + query_params['prop_node_snapshot'] + " = $from_mid "
                "AND m2." + query_params['prop_node_name'] + " = $to_formula AND m2." + query_params['prop_node_snapshot'] + " = $to_mid "
            "SET s." + query_params['prop_extra_10'] + " = $tendency_weight "
        , parameters= {'from_formula': row['from_formula'], 
            'from_mid': row['from_mid'], 
            'to_formula': row['to_formula'], 
            'to_mid': row['to_mid'], 
            'tendency_weight': row['tendency_weight']})

    print('done: add property ' + query_params['prop_extra_10'])

# add the final weights to the graph
def add_weights(session_temporal, upper_limit, lower_limit, query_params):
    tendency_weights = session_temporal.run(
        "MATCH (m1:" + query_params['label_node'] + ")-[prt:" + query_params['label_predicted_edge'] + "]->(m2:" + query_params['label_node'] + "), "
            "(m1)-[s1:" + query_params['label_same_as'] + "]->(:" + query_params['label_node'] + "), "
            "(:" + query_params['label_node'] + ")-[s2:" + query_params['label_same_as'] + "]->(m2) "
        "SET prt." + query_params['prop_extra_11'] + " = s1." + query_params['prop_extra_10'] + " + s2." + query_params['prop_extra_10'] + " "
    ).to_df()

    print('done: add weights to graph')

# normalize incoming weights
def normalize_weights(session_temporal, query_params):
    session_temporal.run(
        "MATCH (:" + query_params['label_node'] + ")-[t:" + query_params['label_predicted_edge'] + "]->(m:" + query_params['label_node'] + ") " 
        "WITH m." + query_params['prop_node_name'] + " as fs, m." + query_params['prop_node_snapshot'] + " as mid, "
            "sum(t." + query_params['prop_extra_11'] + ") as sum_weight "
        "MATCH (:" + query_params['label_node'] + ")-[t1:" + query_params['label_predicted_edge'] + "]->(m1:" + query_params['label_node'] + ") "
        "WHERE m1." + query_params['prop_node_name'] + " = fs AND m1." + query_params['prop_node_snapshot'] + " = mid "
        "SET t1." + query_params['prop_extra_15'] + " = t1." + query_params['prop_extra_11'] + "/sum_weight"
    )

    print('done: normalize weights')

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # establish connection to graph
    session_temporal = pvc.pf.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # calculate weights and add to graph
    tendencies = get_tendencies(session_temporal, pvc.query_params)
    tendency_weights = calc_weights(tendencies, pvc.upper_limit, pvc.lower_limit)
    calc_temp_weights(tendency_weights, session_temporal, pvc.query_params)
    add_weights(session_temporal, pvc.upper_limit, pvc.lower_limit, pvc.query_params)
    normalize_weights(session_temporal, pvc.query_params)

    # close session
    session_temporal.close()