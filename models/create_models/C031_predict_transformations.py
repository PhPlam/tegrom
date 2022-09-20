# Name: Philipp Plamper
# Date: 20. september 2022

import pandas as pd
from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_temporal
from C000_path_variables_create import int_change_path
from C000_path_variables_create import lower_limit, upper_limit


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name = db_name_temporal

# fault tolerance for intensity trend 
lower_limit = lower_limit
upper_limit = upper_limit

# set path
int_change_path = int_change_path # calculated occurring transformations


##################################################################################
#define functions to calculate occurring transformations (RelIdent-Algorithm)#####
##################################################################################

# establish connection to the database
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection


# calculate occurring transformations
def calculate_occurring_transformations(call_graph):
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
        RETURN m2.formula_string as to_molecule, m1.point_in_time as from_mid, m2.point_in_time as to_mid, m3.formula_string as from_molecule, 
        C, H, O, N, S, s2.tendency_weight as tendency_weight_lose, s.tendency_weight as tendency_weight_gain,
        s2.tendency_weight_conn as tendency_weight_lose_conn, s.tendency_weight_conn as tendency_weight_gain_conn
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


# calculate combined and connected weight
def calculate_weights(trans_units, int_change_path):
    trans_units = trans_units   
    
    conn_weight_list = []
    comb_weight_list = []

    for row in trans_units.itertuples():
        comb_erg = (row.tendency_weight_lose + row.tendency_weight_gain)
        conn_erg = (row.tendency_weight_lose_conn + row.tendency_weight_gain_conn)
        
        comb_weight_list.append(comb_erg)
        conn_weight_list.append(conn_erg)
        
    trans_units['weight_combined'] = comb_weight_list
    trans_units['weight_connected'] = conn_weight_list

    # add weights to csv with calculated occurring transformations 
    trans_units.to_csv(int_change_path, sep=',', encoding='utf-8', index=False)

    print('done: calculate combined and connected weight')
    return trans_units


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
                transformation_unit: $transformation_unit, 
                combined_weight: toFloat($weight_combined), 
                connected_weight: toFloat($weight_connected)}]->(m2)
        """, parameters= {'from_molecule': row['from_molecule'], 'from_mid': row['from_mid'], 
        'to_molecule': row['to_molecule'], 'to_mid': row['to_mid'], 'C': row['C'], 'H': row['H'], 
        'O': row['O'], 'N': row['N'], 'S': row['S'], 'transformation_unit': row['transformation_unit'], 
        'weight_combined': row['weight_combined'], 'weight_connected': row['weight_connected']
        })        
    graph.commit(tx) 

    print('done: create PREDICTED_TRANSFORMATION relationship')


# normalize incoming combined and connected weight
def normalize_weights(call_graph):
    graph = call_graph
    graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(m:Molecule)
        WITH m.formula_string as fs, m.point_in_time as mid, sum(t.connected_weight) as sum_weight
        MATCH (:Molecule)-[t1:PREDICTED_TRANSFORMATION]->(m1:Molecule)
        WHERE m1.formula_string = fs AND m1.point_in_time = mid
        SET t1.normalized_connected_weight = apoc.math.round(t1.connected_weight/sum_weight, 3)
        RETURN fs, mid, sum_weight
    """)

    graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(m:Molecule)
        WITH m.formula_string as fs, m.point_in_time as mid, sum(t.combined_weight) as sum_weight
        MATCH (:Molecule)-[t1:PREDICTED_TRANSFORMATION]->(m1:Molecule)
        WHERE m1.formula_string = fs AND m1.point_in_time = mid
        SET t1.normalized_combined_weight = apoc.math.round(t1.combined_weight/sum_weight, 3)
        RETURN fs, mid, sum_weight
    """)

    print('done: normalize weights')


##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = get_database_connection(host, user, passwd, db_name)

# calculate and add occurring transformations (RelIdent-Algorithm)
occ_trans = calculate_occurring_transformations(call_graph)
trans_units = calculate_transformation_units(occ_trans)
calc_weights = calculate_weights(trans_units, int_change_path)
create_relationship_predicted_transformation(call_graph, calc_weights)
normalize_weights(call_graph)
