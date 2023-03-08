# Name: Philipp Plamper
# Date: 24. january 2023

import pandas as pd
from neo4j import GraphDatabase
import C000_path_variables_create as pvc

###################################################################################
#define functions to predict likely occurring transformations (RelIdent-Algorithm)#
###################################################################################

# predict likely occurring transformations
# Transformation Prediction Algorithm
def predict_likely_occurring_transformations(session, upper_limit, lower_limit, query_params):
    increasing_intensity_df = session.run(
        "MATCH (m1:" + query_params['label_node'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + ") "
        "WHERE s." + query_params['prop_edge_value_2'] + " > " + str(upper_limit) + 
            " AND m1." + query_params['prop_node_snapshot'] + " = m2." + query_params['prop_node_snapshot'] + " - 1 "
        "WITH m1, m2, s "
        "MATCH (m3:" + query_params['label_node'] + ")-[pot:" + query_params['label_potential_edge'] + "]->(m2) "
        "WHERE m3." + query_params['prop_node_snapshot'] + " = m1." + query_params['prop_node_snapshot'] +
        " WITH m3, m2, m1, s, pot "
        "MATCH (m3)-[s2:" + query_params['label_same_as'] + "]->(m4:" + query_params['label_node'] + ") "
        "WHERE s2." + query_params['prop_edge_value_2'] + " < " + str(lower_limit) +
            " AND m3." + query_params['prop_node_snapshot'] + " = m1." + query_params['prop_node_snapshot'] +
            " AND m4." + query_params['prop_node_snapshot'] + " = m2." + query_params['prop_node_snapshot'] +
        " WITH m2." + query_params['prop_extra_1'] + " - m3." + query_params['prop_extra_1'] + " as C, " 
            "m2." + query_params['prop_extra_2'] + " - m3." + query_params['prop_extra_2'] + " as H, " 
            "m2." + query_params['prop_extra_3'] + " - m3." + query_params['prop_extra_3'] + " as N, "
            "m2." + query_params['prop_extra_4'] + " - m3." + query_params['prop_extra_4'] + " as O, " 
            "m2." + query_params['prop_extra_5'] + " - m3." + query_params['prop_extra_5'] + " as S, "
            "m2, m3, m1, s, s2, pot "
        "RETURN  m3." + query_params['prop_node_name'] + " as from_node, "
            "m2." + query_params['prop_node_name'] + " as to_node, "
            "m1." + query_params['prop_node_snapshot'] + " as from_time, " 
            "m2." + query_params['prop_node_snapshot'] + " as to_time, " 
            "pot." + query_params['prop_extra_13'] + " as is_addition, "
            "C, H, N, O, S"
    ).to_df()

    print('done: predict likely occurring transformations')
    return increasing_intensity_df


# take predicted likely occurring transformations and create strings of transformation units
def calculate_transformation_units(occ_trans, query_params):
    tu_list = []
    
    for row in occ_trans.itertuples(): # index=False
        tu_string = ""

        if row.C < 0: tu_string = "-" + tu_string + "C" + str(abs(row.C)) + " "
        elif row.C > 0: tu_string = tu_string + "C" + str(row.C) + " "
        else: tu_string

        if row.H < 0: tu_string = tu_string + "-H" + str(abs(row.H)) + " "
        elif row.H > 0: tu_string = tu_string + "H" + str(row.H) + " "
        else: tu_string

        if row.O < 0: tu_string = tu_string + "-O" + str(abs(row.O)) + " "
        elif row.O > 0: tu_string = tu_string + "O" + str(row.O) + " "
        else: tu_string

        if row.N < 0: tu_string = tu_string + "-N" + str(abs(row.N)) + " "
        elif row.N > 0: tu_string = tu_string + "N" + str(row.N) + " "
        else: tu_string

        if row.S < 0: tu_string = tu_string + "-S" + str(abs(row.S)) + " "
        elif row.S > 0: tu_string = tu_string + "S" + str(row.S) + " "
        else: tu_string

        tu_string = tu_string.rstrip()
        tu_list.append(tu_string)
    
    occ_trans['edge_string'] = tu_list
    
    print('done: calculate strings '+ query_params['prop_edge_value_1'])
    return occ_trans

# create relationship PREDICTED_TRANSFORMATION with calculated occurring transformations
def create_relationship_predicted_transformation(session, calc_weights, query_params):
    for index, row in calc_weights.iterrows():
        session.run(
            "MATCH (m1:" + query_params['label_node'] + "), (m2:" + query_params['label_node'] + ") "
            "WHERE m1." + query_params['prop_node_name'] + " = $from_node "
                "AND m2." + query_params['prop_node_name'] + " = $to_node "
                "AND m1." + query_params['prop_node_snapshot'] + " = $from_time "
                "AND m2." + query_params['prop_node_snapshot'] + " = $to_time "
            "CREATE (m1)-[:" + query_params['label_predicted_edge'] + " { "
                + query_params['prop_extra_1'] + ": toInteger($C), " 
                + query_params['prop_extra_2'] + ": toInteger($H), " 
                + query_params['prop_extra_3'] + ": toInteger($N), "
                + query_params['prop_extra_4'] + ": toInteger($O), "  
                + query_params['prop_extra_5'] + ": toInteger($S), " 
                + query_params['prop_extra_13'] + ": toInteger($is_addition), "
                + query_params['prop_edge_value_1'] + ": $edge_string}]->(m2) "
        , parameters= {'from_node' : row['from_node'], 
                            'to_node' : row['to_node'],
                            'from_time' : row['from_time'],  
                            'to_time' : row['to_time'], 
                            'C' : row['C'], 
                            'H' : row['H'], 
                            'N' : row['N'], 
                            'O' : row['O'], 
                            'S' : row['S'], 
                            'is_addition' : row['is_addition'],
                            'edge_string' : row['edge_string']
        })        

    print('done: create relationship ' + query_params['label_predicted_edge'])

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # establish connection to graph
    session = pvc.pf.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # calculate and add predicted likely occurring transformations (Transformation Prediction Algorithm)
    occ_trans = predict_likely_occurring_transformations(session, pvc.upper_limit, pvc.lower_limit, pvc.query_params)
    trans_units = calculate_transformation_units(occ_trans, pvc.query_params)
    create_relationship_predicted_transformation(session, trans_units, pvc.query_params)

    # close session
    session.close()