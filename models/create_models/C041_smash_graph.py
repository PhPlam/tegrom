# Name: Philipp Plamper 
# Date: 11. november 2022

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
        RETURN m1.""" + query_params['prop_node_name'] + """ as from_node, 
        m1.""" + query_params['prop_node_value'] + """ as from_node_value, 
        m1.""" + query_params['prop_node_snapshot'] + """ as from_node_time, 
        s1.""" + query_params['prop_edge_value_2'] + """ as from_node_edge_value, 
        m2.""" + query_params['prop_node_name'] + """ as to_node, 
        m2.""" + query_params['prop_node_value'] + """ as to_node_value, 
        m2.""" + query_params['prop_node_snapshot'] + """ as to_node_time, 
        s2.""" + query_params['prop_edge_value_2'] + """ as to_node_edge_value, 
        p.""" + query_params['prop_edge_value_1'] + """ as edge_string
    """).to_data_frame()

    # fill null values of columns matched with 'Optional Match'
    new_model_paths = new_model_paths.fillna(0)

    print('done: get all edges ' + query_params['label_potential_edge'])

    return new_model_paths


# create molecule nodes from unique formula strings
def create_nodes_molecule(call_graph_par, call_graph_com, query_params):
    df_unique_mol = call_graph_par.run("""
    MATCH (m:""" + query_params['label_node'] + """)
    RETURN m.""" + query_params['prop_node_name'] + """ as node_string, 
        m.""" + query_params['prop_extra_1'] + """ as C, 
        m.""" + query_params['prop_extra_2'] + """ as H, 
        m.""" + query_params['prop_extra_3'] + """ as N, 
        m.""" + query_params['prop_extra_4'] + """ as O, 
        m.""" + query_params['prop_extra_5'] + """ as S,
        m.""" + query_params['prop_extra_4'] + query_params['prop_extra_1'] + """ as OC,
        m.""" + query_params['prop_extra_2'] + query_params['prop_extra_1'] + """ as HC,
        count(m) as cnt 
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_unique_mol.iterrows():
        tx.evaluate("""
            CREATE (:""" + query_params['label_node'] + """ {""" + query_params['prop_node_name'] + """:$node_string,         
                    """ + query_params['prop_extra_1'] + """ : toInteger($C), 
                    """ + query_params['prop_extra_2'] + """ : toInteger($H), 
                    """ + query_params['prop_extra_3'] + """ : toInteger($N), 
                    """ + query_params['prop_extra_4'] + """ : toInteger($O), 
                    """ + query_params['prop_extra_5'] + """ : toInteger($S),
                    """ + query_params['prop_extra_4'] + query_params['prop_extra_1'] + """ : toFloat($OC),
                    """ + query_params['prop_extra_2'] + query_params['prop_extra_1'] + """ : toFloat($HC)})
            RETURN count(*) 
        """, parameters= {'node_string' : row['node_string'], 
                            'C' : row['C'],
                            'H' : row['H'], 
                            'N' : row['N'], 
                            'O' : row['O'], 
                            'S' : row['S'],
                            'OC' : row['OC'],
                            'HC' : row['HC']
                            })
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
    RETURN  m1.""" + query_params['prop_node_name'] + """ as from_node, 
        m2.""" + query_params['prop_node_name'] + """ as to_node, 
        pot.""" + query_params['prop_edge_value_1'] + """ as edge_string, 
        pot.""" + query_params['prop_extra_1'] + """ as C, 
        pot.""" + query_params['prop_extra_2'] + """ as H, 
        pot.""" + query_params['prop_extra_3'] + """ as N,
        pot.""" + query_params['prop_extra_4'] + """ as O,  
        pot.""" + query_params['prop_extra_5'] + """ as S, 
        count(*)
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_pot_rel.iterrows():
        tx.evaluate("""
            MATCH (m1:""" + query_params['label_node'] + """), (m2:""" + query_params['label_node'] + """)
            WHERE m1.""" + query_params['prop_node_name'] + """ = $from_node
                AND m2.""" + query_params['prop_node_name'] + """ = $to_node
            CREATE (m1)-[:""" + query_params['label_chemical_edge'] + """ {
                """ + query_params['prop_edge_value_1'] + """ : $edge_string, 
                """ + query_params['prop_extra_1'] + """ : $C, 
                """ + query_params['prop_extra_2'] + """ : $H, 
                """ + query_params['prop_extra_3'] + """ : $N, 
                """ + query_params['prop_extra_4'] + """ : $O, 
                """ + query_params['prop_extra_5'] + """ : $S}]->(m2)
            RETURN count(*)
        """, parameters= {'from_node' : row['from_node'], 
                            'to_node' : row['to_node'], 
                            'C' : row['C'], 
                            'H' : row['H'], 
                            'N' : row['N'],
                            'O' : row['O'],  
                            'S' : row['S'], 
                            'edge_string' : row['edge_string']
                            })
    call_graph_com.commit(tx)

    print('done: create relationship ' + query_params['label_chemical_edge'])


# create and set properties at relationship CHEMICAL_TRANSRFORMATION
def set_properties_chemical_transformation(call_graph_com, new_model_paths, query_params):
    for i in range (1,new_model_paths['to_node_time'].max()+1):
        is_prt_list = []
        new_model_paths_trim = new_model_paths[new_model_paths['to_node_time'] == i]
        
        for row in new_model_paths_trim.itertuples():
            if (0 < getattr(row, 'from_node_edge_value') < 0.975 and getattr(row, 'to_node_edge_value') > 1.025):
                is_prt_list.append(1)
            else:
                is_prt_list.append(0)
        new_model_paths_trim['predicted'] = is_prt_list

        tx = call_graph_com.begin()
        for index, row in new_model_paths_trim.iterrows():
            tx.evaluate("""
                MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(m2:""" + query_params['label_node'] + """)
                WHERE m1.""" + query_params['prop_node_name'] + """ = $from_node
                    AND m2.""" + query_params['prop_node_name'] + """ = $to_node
                    AND c.""" + query_params['prop_edge_value_1'] + """ = $edge_string
                SET c.transition_""" + str(i) + """ = 
                    [toFloat($to_node_time), 
                    toFloat($from_node_value), 
                    toFloat($to_node_value), 
                    toFloat($from_node_edge_value), 
                    toFloat($to_node_edge_value), 
                    toFloat($predicted)]        
            """, parameters= {'from_node' : row['from_node'], 
                                'to_node' : row['to_node'], 
                                'edge_string' : row['edge_string'],
                                'to_node_time' : row['to_node_time'], 
                                'from_node_value' : row['from_node_value'], 
                                'to_node_value' : row['to_node_value'],
                                'from_node_edge_value' : row['from_node_edge_value'], 
                                'to_node_edge_value' : row['to_node_edge_value'],
                                'predicted': row.predicted}
            )
        call_graph_com.commit(tx)
        print('done: set properties of transition:', str(i))
    
    print('done: set properties at relationship ' + query_params['label_chemical_edge'])
        
    # order of properties in List
    # 1. transition
    # 2. normalized intensity of source molecule
    # 3. normalized intensity of target molecule
    # 4. intensity trend to molecule with same formula of source molecule
    # 5. intensity trend from molecule with same formula of target molecule
    # 6. is prt, see "Transformation Prediction Algorithm"


# property 'transition_count'
# = number of transtions between two molecules 
def create_property_transition_count(call_graph, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
        WITH m1, c, size(keys(c))-6 as keys
        SET c.""" + query_params['prop_extra_8'] + """ = keys
        RETURN m1.""" + query_params['prop_node_name'] + """, keys LIMIT 5
    """)

    print('done: create property ' + query_params['prop_extra_8'])


# property 'prt_count'
# = number of transtions recognizes as edge of type 'prt' 
def create_property_prt_count(call_graph, new_model_paths, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
        SET c.""" + query_params['prop_extra_9'] + """ = 0
        RETURN count(*)
    """)

    for i in range(1,new_model_paths['to_node_time'].max()+1):
        call_graph.run("""
            MATCH (m1:""" + query_params['label_node'] + """)-[c:""" + query_params['label_chemical_edge'] + """]->(:""" + query_params['label_node'] + """)
            WHERE c.transition_""" + str(i) + """[5] = 1
            SET c.""" + query_params['prop_extra_9'] + """ = c.""" + query_params['prop_extra_9'] + """ + 1
            RETURN count(*)
        """)

    print('done: create property ' + query_params['prop_extra_9'])
    
### for graph with ###
### only prt edges ###

# delete edges with prt_count = 0
# MATCH (:Molecule)-[ct:CHEMICAL_TRANSFORMATION]->(:Molecule)
# WHERE ct.prt_count = 0
# DELETE ct

# delete nodes with no edges 
# MATCH (m:Molecule)
# WHERE NOT EXISTS ((m)-[:CHEMICAL_TRANSFORMATION]-(:Molecule))
# DELETE m

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
