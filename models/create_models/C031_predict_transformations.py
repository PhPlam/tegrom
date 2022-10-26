# Name: Philipp Plamper
# Date: 26.october 2022

import pandas as pd
from py2neo import Graph
import C000_path_variables_create as pvc

##################################################################################
#define functions to calculate occurring transformations (RelIdent-Algorithm)#####
##################################################################################

# calculate occurring transformations
def calculate_occurring_transformations(call_graph, upper_limit, lower_limit):
    graph = call_graph
    increasing_intensity_df = graph.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend > """ + str(upper_limit) + """ AND m1.point_in_time = m2.point_in_time - 1
        WITH m1, m2, s
        MATCH (m3:Molecule)-[:POTENTIAL_TRANSFORMATION]->(m2)
        WHERE m3.point_in_time = m1.point_in_time
        WITH m3, m2, m1, s
        MATCH (m3)-[s2:SAME_AS]->(m4:Molecule)
        WHERE s2.intensity_trend < """ + str(lower_limit) + """
        AND m3.point_in_time = m1.point_in_time 
        AND m4.point_in_time = m2.point_in_time
        WITH m2.C - m3.C as C, m2.H - m3.H as H, m2.O - m3.O as O, m2.N - m3.N as N, m2.S - m3.S as S, m2, m3, m1, s, s2
        RETURN m2.formula_string as to_molecule, m1.point_in_time as from_mid, 
            m2.point_in_time as to_mid, m3.formula_string as from_molecule, C, H, O, N, S
    """).to_data_frame()
    
    print('done: calculate occurring transformations')
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
def create_relationship_predicted_transformation(call_graph, calc_weights):
    calc_weights = calc_weights
    graph = call_graph

    tx = graph.begin()
    for index, row in calc_weights.iterrows():
        tx.evaluate("""
            MATCH (m1:Molecule), (m2:Molecule)
            WHERE m1.formula_string = $from_molecule
                AND m1.point_in_time = $from_mid
                AND m2.formula_string = $to_molecule
                AND m2.point_in_time = $to_mid
            CREATE (m1)-[:PREDICTED_TRANSFORMATION {C: toInteger($C), 
                H: toInteger($H), 
                O: toInteger($O), 
                N: toInteger($N), 
                S: toInteger($S), 
                transformation_unit: $transformation_unit}]->(m2)
        """, parameters= {'from_molecule': row['from_molecule'], 'from_mid': row['from_mid'], 
        'to_molecule': row['to_molecule'], 'to_mid': row['to_mid'], 'C': row['C'], 'H': row['H'], 
        'O': row['O'], 'N': row['N'], 'S': row['S'], 'transformation_unit': row['transformation_unit']
        })        
    graph.commit(tx) 

    print('done: create PREDICTED_TRANSFORMATION relationship')

##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

# calculate and add occurring transformations (RelIdent-Algorithm)
occ_trans = calculate_occurring_transformations(call_graph, pvc.upper_limit, pvc.lower_limit)
trans_units = calculate_transformation_units(occ_trans)
create_relationship_predicted_transformation(call_graph, trans_units)
