# Name: Philipp Plamper
# Date: 27.october 2022

import pandas as pd
from py2neo import Graph
import C000_path_variables_create as pvc

##################################################################################
#define functions to calculate occurring transformations (RelIdent-Algorithm)#####
##################################################################################

# calculate occurring transformations
def calculate_occurring_transformations(call_graph, upper_limit, lower_limit, query_params):
    graph = call_graph
    increasing_intensity_df = graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[s:""" + query_params['label_same_as'] + """]->(m2:""" + query_params['label_node'] + """)
        WHERE s.""" + query_params['prop_edge_value_2'] + """ > """ + str(upper_limit) + """ 
            AND m1.""" + query_params['prop_node_snapshot'] + """ = m2.""" + query_params['prop_node_snapshot'] + """ - 1
        WITH m1, m2, s
        MATCH (m3:""" + query_params['label_node'] + """)-[:""" + query_params['label_potential_edge'] + """]->(m2)
        WHERE m3.""" + query_params['prop_node_snapshot'] + """ = m1.""" + query_params['prop_node_snapshot'] + """
        WITH m3, m2, m1, s
        MATCH (m3)-[s2:""" + query_params['label_same_as'] + """]->(m4:""" + query_params['label_node'] + """)
        WHERE s2.""" + query_params['prop_edge_value_2'] + """ < """ + str(lower_limit) + """
        AND m3.""" + query_params['prop_node_snapshot'] + """ = m1.""" + query_params['prop_node_snapshot'] + """
        AND m4.""" + query_params['prop_node_snapshot'] + """ = m2.""" + query_params['prop_node_snapshot'] + """
        WITH m2.""" + query_params['prop_extra_1'] + """ - m3.""" + query_params['prop_extra_1'] + """ as """ + query_params['prop_extra_1'] + """, 
            m2.""" + query_params['prop_extra_2'] + """ - m3.""" + query_params['prop_extra_2'] + """ as """ + query_params['prop_extra_2'] + """, 
            m2.""" + query_params['prop_extra_3'] + """ - m3.""" + query_params['prop_extra_3'] + """ as """ + query_params['prop_extra_3'] + """,
            m2.""" + query_params['prop_extra_4'] + """ - m3.""" + query_params['prop_extra_4'] + """ as """ + query_params['prop_extra_4'] + """,  
            m2.""" + query_params['prop_extra_5'] + """ - m3.""" + query_params['prop_extra_5'] + """ as """ + query_params['prop_extra_5'] + """, 
            m2, m3, m1, s, s2
        RETURN m2.""" + query_params['prop_node_name'] + """ as to_molecule, m1.""" + query_params['prop_node_snapshot'] + """ as from_mid, 
            m2.""" + query_params['prop_node_snapshot'] + """ as to_mid, m3.""" + query_params['prop_node_name'] + """ as from_molecule, C, H, O, N, S
    """).to_data_frame()
    
    print('done: calculate likely occurring transformations')
    return increasing_intensity_df


# take calculated occurring transformations and create strings of transformation units
def calculate_transformation_units(occ_trans):
    occ_trans = occ_trans
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
    
    occ_trans['transformation_unit'] = tu_list
    
    print('done: calculate transformation unit strings')
    return occ_trans

# create relationship PREDICTED_TRANSFORMATION with calculated occurring transformations
def create_relationship_predicted_transformation(call_graph, calc_weights, query_params):
    calc_weights = calc_weights
    graph = call_graph

    tx = graph.begin()
    for index, row in calc_weights.iterrows():
        tx.evaluate("""
            MATCH (m1:""" + query_params['label_node'] + """), (m2:""" + query_params['label_node'] + """)
            WHERE m1.""" + query_params['prop_node_name'] + """ = $from_molecule
                AND m1.""" + query_params['prop_node_snapshot'] + """ = $from_mid
                AND m2.""" + query_params['prop_node_name'] + """ = $to_molecule
                AND m2.""" + query_params['prop_node_snapshot'] + """ = $to_mid
            CREATE (m1)-[:""" + query_params['label_predicted_edge'] + """ {
                """ + query_params['prop_extra_1'] + """: toInteger($C), 
                """ + query_params['prop_extra_2'] + """: toInteger($H), 
                """ + query_params['prop_extra_3'] + """: toInteger($N),
                """ + query_params['prop_extra_4'] + """: toInteger($O),  
                """ + query_params['prop_extra_5'] + """: toInteger($S), 
                """ + query_params['prop_edge_value_1'] + """: $transformation_unit}]->(m2)
        """, parameters= {'from_molecule': row['from_molecule'], 'from_mid': row['from_mid'], 
        'to_molecule': row['to_molecule'], 'to_mid': row['to_mid'], 'C': row['C'], 'H': row['H'], 
        'O': row['O'], 'N': row['N'], 'S': row['S'], 'transformation_unit': row['transformation_unit']
        })        
    graph.commit(tx) 

    print('done: create ' + query_params['label_predicted_edge'] + ' relationship')

##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

# calculate and add occurring transformations (RelIdent-Algorithm)
occ_trans = calculate_occurring_transformations(call_graph, pvc.upper_limit, pvc.lower_limit, pvc.query_params)
trans_units = calculate_transformation_units(occ_trans)
create_relationship_predicted_transformation(call_graph, trans_units, pvc.query_params)
