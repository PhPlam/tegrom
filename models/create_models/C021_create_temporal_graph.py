# Name: Philipp Plamper 
# Date: 06. april 2023

import os
import time
from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create the nodes 
def create_nodes_molecule(session, formula_file_path, query_params):
    session.run(
        "LOAD CSV WITH HEADERS FROM 'file:///" + formula_file_path + "' AS row "
        "CREATE (m:" + query_params['label_node'] + query_params['nodes_temporal'] + " { "
         + query_params['prop_node_name'] + " : row.formula_string, "
         + query_params['prop_node_value'] + " : toFloat(row.peak_relint_tic), "
         + query_params['prop_node_snapshot'] + " : toInteger(row.timepoint), "
         + query_params['prop_extra_1'] + " : toInteger(row.C), "
         + query_params['prop_extra_2'] + " : toInteger(row.H), "
         + query_params['prop_extra_3'] + " : toInteger(row.N), "
         + query_params['prop_extra_4'] + " : toInteger(row.O), "
         + query_params['prop_extra_5'] + " : toInteger(row.S), "
         + query_params['prop_extra_4'] + query_params['prop_extra_1'] + " : toFloat(row.O)/toFloat(row.C), "
         + query_params['prop_extra_2'] + query_params['prop_extra_1'] + " : toFloat(row.H)/toFloat(row.C), "
         # radiation_dose only added if exists, if not in data no action needed
         + query_params['prop_extra_12'] + " : toFloat(row.radiation_dose), "
         # formula_class removed -> not in current model
         # + query_params['prop_extra_14'] + " : row.formula_class, "
         + query_params['prop_extra_16'] + " : toInteger(row.formula_mass_nominal)})"
    )
    print('done: create ' + query_params['label_node'] + query_params['nodes_temporal'] + ' nodes')

# create constraint molecular_formula in combination with point in time is unique
def create_contraint(session, query_params):
    session.run(
        "CREATE CONSTRAINT FOR (m" 
        + query_params['nodes_temporal'] + ") REQUIRE (m." 
        + query_params['prop_node_name'] + ", m." 
        + query_params['prop_node_snapshot'] + ") IS NODE KEY"
    )
    print('done: create unique ' + query_params['prop_node_name'] + ' constraint')

# create index on formula strings
def create_index(session, query_params):
    session.run("CREATE INDEX FOR (m" 
        + query_params['nodes_temporal'] + ") ON (m." 
        + query_params['prop_node_name'] + ")")
    print('done: create index on ' + query_params['prop_node_name'])

# create POTENTIAL TRANSFORMATION relationship
def create_relationship_potential_transformation(session, transform_file_path, query_params):
    session.run(
        "CALL apoc.periodic.iterate("
        "'LOAD CSV WITH HEADERS FROM \"file:///" + transform_file_path + "\" AS row RETURN row', "
        "'WITH row.new_formula AS to_node, "
            "row.formula_string AS from_node, "
            "row.tu_C AS C, "
            "row.tu_H AS H, "
            "row.tu_N AS N, "
            "row.tu_O AS O, " 
            "row.tu_S AS S, "
            "row.is_addition AS is_addition, "
            "row.transformation_unit as transformation_unit "
        "MATCH (m:" + query_params['label_node'] + query_params['nodes_temporal'] + "), (m2:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "WHERE m." + query_params['prop_node_name'] + " = from_node "
            "AND m2." + query_params['prop_node_name'] + " = to_node "
            "AND m." + query_params['prop_node_snapshot'] + " = m2." + query_params['prop_node_snapshot'] + "-1 "
        "CREATE (m)-[:" + query_params['label_potential_edge'] + "{ "
            + query_params['prop_extra_1'] + ": toInteger(C), "
            + query_params['prop_extra_2'] + ": toInteger(H), "
            + query_params['prop_extra_3'] + ": toInteger(N), "
            + query_params['prop_extra_4'] + ": toInteger(O), "
            + query_params['prop_extra_5'] + ": toInteger(S), "
            + query_params['prop_extra_13'] + ": toInteger(is_addition), "
            + query_params['prop_edge_value_1'] + ": transformation_unit}]->(m2) "
        "RETURN count(*)', "
        "{batchSize: 500})"
    )
    print('done: create ' + query_params['label_potential_edge'] + ' relationship')

# create SAME_AS relationship
def create_relationship_same_as(session, query_params):
    session.run(
        "MATCH (m1:" + query_params['label_node'] + query_params['nodes_temporal'] + "), (m2:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "WHERE m2." + query_params['prop_node_name'] + " = m1." + query_params['prop_node_name'] + " " 
            "AND m2." + query_params['prop_node_snapshot'] + " = m1." + query_params['prop_node_snapshot'] + " + 1 "
        "CREATE (m1)-[:" + query_params['label_same_as'] + "]->(m2)"
    )
    print('done: create ' + query_params['label_same_as'] + ' relationship')

# create intensity_trend property
def create_property_intensity_trend(session, query_params):
    session.run(
        "MATCH (m1:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "WITH (m2." + query_params['prop_node_value'] + "/m1." + query_params['prop_node_value'] + ") as trend, m1, m2, s "
        "SET s." + query_params['prop_edge_value_2'] + " = round(trend, 3) "
    )
    print('done: create property ' + query_params['prop_edge_value_2'])


# delete molecules without edges of type pot
def delete_molecules_without_transformation(session, query_params):
    session.run(
        "MATCH (m:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "WHERE NOT EXISTS ((m)-[:" + query_params['label_potential_edge'] + "]->(:" + query_params['label_node'] + query_params['nodes_temporal'] + ")) "
        "AND NOT EXISTS ((:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[:" + query_params['label_potential_edge'] + "]->(m)) "
        "DETACH DELETE m"
    )

    print("done: delete " + query_params['label_node'] + query_params['nodes_temporal'] + " without edges of type " + query_params['label_potential_edge'])


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create database and establish connection
    #pvc.create_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)
    # wait a few seconds for database creation
    time.sleep(5)
    session = pvc.pf.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # create graph
    create_nodes_molecule(session, pvc.formula_file_path, pvc.query_params)
    create_contraint(session, pvc.query_params)
    create_index(session, pvc.query_params)
    create_relationship_potential_transformation(session, pvc.transform_file_path, pvc.query_params)
    create_relationship_same_as(session, pvc.query_params)
    create_property_intensity_trend(session, pvc.query_params)
    delete_molecules_without_transformation(session, pvc.query_params)

    # close session
    session.close()