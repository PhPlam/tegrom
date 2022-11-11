# Name: Philipp Plamper 
# Date: 11. november 2022

import os
from py2neo import Graph
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create the nodes 
def create_nodes_molecule(call_graph, formula_file_path, query_params):
    graph = call_graph
    graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + formula_file_path + """' AS row
        //FIELDTERMINATOR ';'
        CREATE (:""" + query_params['label_node'] + """ { 
        """ + query_params['prop_node_name'] + """ : row.formula_string, 
        """ + query_params['prop_node_value'] + """ : toFloat(row.peak_relint_tic),
        """ + query_params['prop_node_snapshot'] + """ : toInteger(row.timepoint),
        """ + query_params['prop_extra_1'] + """ : toInteger(row.C), 
        """ + query_params['prop_extra_2'] + """ : toInteger(row.H), 
        """ + query_params['prop_extra_3'] + """ : toInteger(row.N),
        """ + query_params['prop_extra_4'] + """ : toInteger(row.O),  
        """ + query_params['prop_extra_5'] + """ : toInteger(row.S),
        """ + query_params['prop_extra_4'] + query_params['prop_extra_1'] + """ : toFloat(row.O)/toFloat(row.C),
        """ + query_params['prop_extra_2'] + query_params['prop_extra_1'] + """ : toFloat(row.H)/toFloat(row.C)
        })
    """)
    print('done: create ' + query_params['label_node'] + ' nodes')

# create constraint molecular_formula in combination with point in time is unique
def create_contraint(call_graph, query_params):
    graph = call_graph
    graph.run("""CREATE CONSTRAINT ON (m:""" + query_params['label_node'] 
        + """) ASSERT (m.""" + query_params['prop_node_name'] 
        + """, m.""" + query_params['prop_node_snapshot'] + """) IS NODE KEY""")
    print('done: create unique ' + query_params['prop_node_name'] + ' constraint')

# create index on formula strings
def create_index(call_graph, query_params):
    graph = call_graph
    graph.run("""CREATE INDEX FOR (m:""" + query_params['label_node'] + """) ON (m.""" + query_params['prop_node_name'] + """)""")
    print('done: create index on ' + query_params['prop_node_name'])

# create POTENTIAL TRANSFORMATION relationship
def create_relationship_potential_transformation(call_graph, transform_file_path, query_params):
    call_graph.run("""
        CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:///""" + transform_file_path + """' AS row RETURN row",
        "WITH row.new_formula AS from_node, 
            row.formula_string AS to_node, 
            row.tu_C AS C, 
            row.tu_H AS H, 
            row.tu_N AS N,
            row.tu_O AS O,  
            row.tu_S AS S, 
            row.transformation_unit as transformation_unit
        MATCH (m:""" + query_params['label_node'] + """), (m2:""" + query_params['label_node'] + """)
        WHERE m.""" + query_params['prop_node_name'] + """ = from_node 
            AND m2.""" + query_params['prop_node_name'] + """ = to_node
            AND m.""" + query_params['prop_node_snapshot'] + """ = m2.""" + query_params['prop_node_snapshot'] + """-1
        CREATE (m)-[:""" + query_params['label_potential_edge'] + """{
            """ + query_params['prop_extra_1'] + """: toInteger(C), 
            """ + query_params['prop_extra_2'] + """: toInteger(H), 
            """ + query_params['prop_extra_3'] + """: toInteger(N), 
            """ + query_params['prop_extra_4'] + """: toInteger(O), 
            """ + query_params['prop_extra_5'] + """: toInteger(S), 
            """ + query_params['prop_edge_value_1'] + """: transformation_unit}]->(m2)
        RETURN count(*)",
        {batchSize: 500})
    """)
    print('done: create ' + query_params['label_potential_edge'] + ' relationship')

# create SAME_AS relationship
def create_relationship_same_as(call_graph, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """), (m2:""" + query_params['label_node'] + """)
        WHERE m2.""" + query_params['prop_node_name'] + """ = m1.""" + query_params['prop_node_name'] + """ 
            AND m2.""" + query_params['prop_node_snapshot'] + """ = m1.""" + query_params['prop_node_snapshot'] + """ + 1
        CREATE (m1)-[:""" + query_params['label_same_as'] + """]->(m2)
    """)
    print('done: create ' + query_params['label_same_as'] + ' relationship')

# create intensity_trend property
def create_property_intensity_trend(call_graph, query_params):
    call_graph.run("""
        MATCH (m1:""" + query_params['label_node'] + """)-[s:""" + query_params['label_same_as'] + """]->(m2:""" + query_params['label_node'] + """)
        WITH (m2.""" + query_params['prop_node_value'] + """/m1.""" + query_params['prop_node_value'] + """) as trend, 
            m1, m2, s
        SET s.""" + query_params['prop_edge_value_2'] + """ = apoc.math.round(trend, 3)
    """)
    print('done: create property ' + query_params['prop_edge_value_2'])


# delete molecules without edges of type pot
def delete_molecules_wo_pot(call_graph, query_params):
    call_graph.run("""
        MATCH (m:""" + query_params['label_node'] + """)
        WHERE NOT EXISTS ((m)-[:""" + query_params['label_potential_edge'] + """]->(:""" + query_params['label_node'] + """))
        AND NOT EXISTS ((:""" + query_params['label_node'] + """)-[:""" + query_params['label_potential_edge'] + """]->(m))
        DETACH DELETE m
    """)

    print("done: delete " + query_params['label_node'] + " without edges of type " + query_params['label_potential_edge'])


##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
pvc.create_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)
call_graph = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

# create graph
create_nodes_molecule(call_graph, pvc.formula_file_path, pvc.query_params)
create_contraint(call_graph, pvc.query_params)
create_index(call_graph, pvc.query_params)
create_relationship_potential_transformation(call_graph, pvc.transform_file_path, pvc.query_params)
create_relationship_same_as(call_graph, pvc.query_params)
create_property_intensity_trend(call_graph, pvc.query_params)
delete_molecules_wo_pot(call_graph, pvc.query_params)