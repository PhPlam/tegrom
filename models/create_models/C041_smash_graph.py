# Name: Philipp Plamper 
# Date: 04. november 2022

from py2neo import Graph
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################

# deal with not existing "SAME_AS" relationships
# get all pot relationships
def get_relationships(call_graph, query_params):
    new_model_paths = call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[p:""" + query_params['label_potential_edge'] + """]->(m2:""" + query_params['label_node'] + """)
        OPTIONAL MATCH (m1)-[s1:""" + query_params['label_same_as'] + """]->(:""" + query_params['label_node'] + """)
        OPTIONAL MATCH (:""" + query_params['label_node'] + """)-[s2:""" + query_params['label_same_as'] + """]->(m2)
        WHERE m2.""" + query_params['prop_node_snapshot'] + """ = m1.""" + query_params['prop_node_snapshot'] + """ + 1
        RETURN m1.""" + query_params['prop_node_name'] + """ as mol_from, 
        m1.""" + query_params['prop_node_value'] + """ as mol_from_int, 
        m1.""" + query_params['prop_node_snapshot'] + """ as mol_from_time, 
        s1.""" + query_params['prop_edge_value_2'] + """ as mol_from_int_trend, 
        m2.""" + query_params['prop_node_name'] + """ as mol_to, 
        m2.""" + query_params['prop_node_value'] + """ as mol_to_int, 
        m2.""" + query_params['prop_node_snapshot'] + """ as mol_to_time, 
        s2.""" + query_params['prop_edge_value_2'] + """ as mol_to_int_trend, 
        p.""" + query_params['prop_edge_value_1'] + """ as transformation_unit 
    """).to_data_frame()

    # fill null values of columns matched with 'Optional Match'
    new_model_paths = new_model_paths.fillna(0)

    print('done: get all edges ' + query_params['label_potential_edge'])

    return new_model_paths


# create molecule nodes from unique formula strings
def create_nodes_molecule(call_graph_par, call_graph_com, query_params):
    df_unique_mol = call_graph_par.run("""
    MATCH (m:""" + query_params['label_node'] + """)
    RETURN m.""" + query_params['prop_node_name'] + """ as """ + query_params['prop_node_name'] + """, 
        m.""" + query_params['prop_extra_1'] + """ as """ + query_params['prop_extra_1'] + """, 
        m.""" + query_params['prop_extra_2'] + """ as """ + query_params['prop_extra_2'] + """, 
        m.""" + query_params['prop_extra_3'] + """ as """ + query_params['prop_extra_3'] + """, 
        m.""" + query_params['prop_extra_4'] + """ as """ + query_params['prop_extra_4'] + """, 
        m.""" + query_params['prop_extra_5'] + """ as """ + query_params['prop_extra_5'] + """, 
        m.""" + query_params['prop_extra_6'] + """ as """ + query_params['prop_extra_6'] + """, 
        m.""" + query_params['prop_extra_7'] + """ as """ + query_params['prop_extra_7'] + """,
        count(m) as cnt 
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_unique_mol.iterrows():
        tx.evaluate("""
            CREATE (:""" + query_params['label_node'] + """ {""" + query_params['prop_node_name'] + """:$""" + query_params['prop_node_name'] + """,         
                    """ + query_params['prop_extra_1'] + """ : toInteger($""" + query_params['prop_extra_1'] + """), 
                    """ + query_params['prop_extra_2'] + """ : toInteger($""" + query_params['prop_extra_2'] + """), 
                    """ + query_params['prop_extra_3'] + """ : toInteger($""" + query_params['prop_extra_3'] + """), 
                    """ + query_params['prop_extra_4'] + """ : toInteger($""" + query_params['prop_extra_4'] + """), 
                    """ + query_params['prop_extra_5'] + """ : toInteger($""" + query_params['prop_extra_5'] + """),
                    """ + query_params['prop_extra_6'] + """ : toFloat($""" + query_params['prop_extra_6'] + """),
                    """ + query_params['prop_extra_7'] + """ : toFloat($""" + query_params['prop_extra_7'] + """)})
            RETURN count(*) 
        """, parameters= {query_params['prop_node_name'] : row[query_params['prop_node_name']], 
                            'C': row[query_params['prop_extra_1']],
                            'H': row[query_params['prop_extra_2']], 
                            'N': row[query_params['prop_extra_3']], 
                            'O': row[query_params['prop_extra_4']], 
                            'S': row[query_params['prop_extra_5']], 
                            'OC' : row[query_params['prop_extra_6']],
                            'HC' : row[query_params['prop_extra_7']]})
    call_graph_com.commit(tx)

    print('done: create nodes ' + query_params['label_node'])


# create index on formula string
def create_index(call_graph, query_params):
    call_graph.run("""CREATE INDEX FOR (m:""" + query_params['label_node'] + """) ON (m.""" + query_params['prop_node_name'] + """)""")

    print('done: create index on formula string')


# create CHEMICAL_TRANSFORMATION relationship
def create_relationship_chemical_transformation(call_graph_par, call_graph_com, query_params):
    df_pot_rel = call_graph_par.run("""
    MATCH (m1:""" + query_params['label_node'] + """)-[pot:""" + query_params['label_potential_edge'] + """]->(m2:""" + query_params['label_node'] + """)
    RETURN  m1.""" + query_params['prop_node_name'] + """ as from_fs, pot.""" + query_params['prop_edge_value_1'] + """ as tu, 
        m2.""" + query_params['prop_node_name'] + """ as to_fs, pot.C as C, pot.H as H, 
        pot.O as O, pot.N as N, pot.S as S, count(*)
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_pot_rel.iterrows():
        tx.evaluate("""
            MATCH (m1:""" + query_params['label_node'] + """), (m2:""" + query_params['label_node'] + """)
            WHERE m1.""" + query_params['prop_node_name'] + """ = $from_fs 
                AND m2.""" + query_params['prop_node_name'] + """ = $to_fs
            CREATE (m1)-[:""" + query_params['label_chemical_edge'] + """ {tu: $tu, C:$C, H: $H, O: $O, N: $N, S: $S}]->(m2)
            RETURN count(*)
        """, parameters= {'from_fs': row['from_fs'], 'to_fs': row['to_fs'], 'C': row['C'], 
        'H': row['H'], 'O': row['O'], 'N': row['N'], 'S': row['S'], 'tu': row['tu']}
        )
    call_graph_com.commit(tx)

    print('done: create relationship ' + query_params['label_chemical_edge'])


# create and set properties at relationship CHEMICAL_TRANSRFORMATION
def set_properties_chemical_transformation(call_graph_com, new_model_paths, query_params):
    for i in range (1,new_model_paths.mol_to_time.max()+1):
        is_prt_list = []
        new_model_paths_trim = new_model_paths[new_model_paths.mol_to_time == i]
        
        for row in new_model_paths_trim.itertuples():
            if 0 < row.mol_from_int_trend < 0.975 and row.mol_to_int_trend > 1.025:
                is_prt_list.append(1)
            else:
                is_prt_list.append(0)
        new_model_paths_trim['is_prt'] = is_prt_list

        tx = call_graph_com.begin()
        for index, row in new_model_paths_trim.iterrows():
            tx.evaluate("""
                MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(m2:""" + query_params['label_node'] + """)
                WHERE m1.""" + query_params['prop_node_name'] + """ = $mol_from
                    AND m2.""" + query_params['prop_node_name'] + """ = $mol_to
                    AND c.tu = $transformation_unit
                SET c.transition_""" + str(i) + """ = [toFloat($mol_to_time), toFloat($mol_from_int), 
                    toFloat($mol_to_int), toFloat($mol_from_int_trend), 
                    toFloat($mol_to_int_trend), toFloat($is_prt)]        
            """, parameters= {'mol_from': row.mol_from, 'mol_to': row.mol_to, 'transformation_unit': row.transformation_unit,
            'mol_to_time': row.mol_to_time, 'mol_from_int': row.mol_from_int, 'mol_to_int': row.mol_to_int,
            'mol_from_int_trend': row.mol_from_int_trend, 'mol_to_int_trend': row.mol_to_int_trend,
            'is_prt': row.is_prt}
            )
        call_graph_com.commit(tx)
        print('done: set properties of transition:', str(i))
    
    print('done: set properties at relationship chemical transformation')
        
    # order of properties in List
    # 1. transition
    # 2. relative intensity of source molecule
    # 3. relative intensity of target molecule
    # 4. intensity trend to molecule with same formula of source molecule
    # 5. intensity trend from molecule with same formula of target molecule
    # 6. is prt, see RelIdent-algorithm


# property 'transition_count'
# = number of transtions between two molecules 
def create_property_transition_count(call_graph, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
        WITH m1, c, size(keys(c))-6 as keys
        SET c.transition_count = keys
        RETURN m1.""" + query_params['prop_node_name'] + """, keys LIMIT 5
    """)

    print('done: create property transition count')


# property 'prt_count'
# = number of transtions recognizes as edge of type 'prt' 
def create_property_prt_count(call_graph, new_model_paths, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
        SET c.prt_count = 0
        RETURN count(*)
    """)

    for i in range(1,new_model_paths.mol_to_time.max()+1):
        call_graph.run("""
            MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
            WHERE c.transition_""" + str(i) + """[5] = 1
            SET c.prt_count = c.prt_count + 1
            RETURN count(*)
        """)

    print('done: create property prt count')


##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
pvc.create_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_smash)

# connect to parallel model
call_graph_par = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)
new_model_paths = get_relationships(call_graph_par, pvc.query_params)

# connect to compact model
call_graph_com = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_smash)
create_nodes_molecule(call_graph_par, call_graph_com, pvc.query_params)
create_index(call_graph_com, pvc.query_params)
create_relationship_chemical_transformation(call_graph_par, call_graph_com, pvc.query_params)
set_properties_chemical_transformation(call_graph_com, new_model_paths, pvc.query_params)
create_property_transition_count(call_graph_com, pvc.query_params)
create_property_prt_count(call_graph_com, new_model_paths, pvc.query_params)
