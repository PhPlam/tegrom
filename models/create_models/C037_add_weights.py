# Name: Philipp Plamper
# Date: 19.january 2023

import pandas as pd
from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions to calculate occurring transformations (RelIdent-Algorithm)#####
##################################################################################

# calculate occurring transformations
def get_tendency_weights(session_temporal, upper_limit, lower_limit, query_params):
    tendency_weights = session_temporal.run(
        "MATCH (m1:Molecule)-[:PREDICTED_TRANSFORMATION]->(m2:Molecule), "
            "(m1)-[s1:SAME_AS]->(:Molecule), "
            "(:Molecule)-[s2:SAME_AS]->(m2) "
        "RETURN m1.molecular_formula as from_formula, "
            "m1.snapshot as from_snapshot, "
            "m2.molecular_formula as to_formula, "
            "m2.snapshot as to_snapshot, "
            "s1.tendency_weight as tendency_weight_lose, "
            "s2.tendency_weight as tendency_weight_gain, "
            "s1.tendency_weight_conn as tendency_weight_conn_lose, "
            "s2.tendency_weight_conn as tendency_weight_conn_gain"
    ).to_df()
    
    print('get property tendency weights')
    return tendency_weights

# calculate combined and connected weight
def calculate_weights(trans_units):
    trans_units = trans_units   
    
    conn_weight_list = []
    comb_weight_list = []

    for row in trans_units.itertuples():
        comb_erg = (row.tendency_weight_lose + row.tendency_weight_gain)
        conn_erg = (row.tendency_weight_conn_lose + row.tendency_weight_conn_gain)
        
        comb_weight_list.append(comb_erg)
        conn_weight_list.append(conn_erg)
        
    trans_units['weight_combined'] = comb_weight_list
    trans_units['weight_connected'] = conn_weight_list

    print('calculate combined and connected weight')
    return trans_units


# create relationship PREDICTED_TRANSFORMATION with calculated occurring transformations
def add_weights(session_temporal, calc_weights, query_params):
    for index, row in calc_weights.iterrows():
        session_temporal.run(
            "MATCH (m1:Molecule)-[prt:PREDICTED_TRANSFORMATION]->(m2:Molecule) "
            "WHERE m1.molecular_formula = $from_formula "
                "AND m1.snapshot = $from_snapshot "
                "AND m2.molecular_formula = $to_formula "
                "AND m2.snapshot = $to_snapshot "
            "SET prt.combined_weight = toFloat($weight_combined) " 
            "SET prt.connected_weight = toFloat($weight_connected)"
        , parameters= {'from_formula': row['from_formula'], 
            'from_snapshot': row['from_snapshot'], 
            'to_formula': row['to_formula'], 
            'to_snapshot': row['to_snapshot'], 
            'weight_combined': row['weight_combined'], 
            'weight_connected': row['weight_connected']
        })        

    print('add weights')


# normalize incoming combined and connected weight
def normalize_weights(session_temporal, query_params):
    session_temporal.run(
        "MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(m:Molecule) " 
        "WITH m.molecular_formula as fs, m.snapshot as mid, sum(t.connected_weight) as sum_weight "
        "MATCH (:Molecule)-[t1:PREDICTED_TRANSFORMATION]->(m1:Molecule) "
        "WHERE m1.molecular_formula = fs AND m1.snapshot = mid "
        "SET t1.normalized_connected_weight = t1.connected_weight/sum_weight "
        "RETURN fs, mid, sum_weight"
    )

    session_temporal.run(
        "MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(m:Molecule) "
        "WITH m.molecular_formula as fs, m.snapshot as mid, sum(t.combined_weight) as sum_weight "
        "MATCH (:Molecule)-[t1:PREDICTED_TRANSFORMATION]->(m1:Molecule) "
        "WHERE m1.molecular_formula = fs AND m1.snapshot = mid "
        "SET t1.normalized_combined_weight = t1.combined_weight/sum_weight "
        "RETURN fs, mid, sum_weight"
    )

    print('normalize weights')


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # establish connection to graph
    session_temporal = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # calculate and add combined and connected weight to nodes
    tendency_weights = get_tendency_weights(session_temporal, pvc.upper_limit, pvc.lower_limit, pvc.query_params)
    calc_weights = calculate_weights(tendency_weights)
    add_weights(session_temporal, calc_weights, pvc.query_params)
    normalize_weights(session_temporal, pvc.query_params)

    # close session
    session_temporal.close()
