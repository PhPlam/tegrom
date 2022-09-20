# Name: Philipp Plamper 
# Date: 11. july 2022

# be sure your neo4j instance is up and running
# configure custom filepaths, see requirements (comment out 'dbms.directories.import=import' in neo4j settings)

import os
from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_temporal
from C000_path_variables_create import formula_file_path, transform_file_path


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name = db_name_temporal

# path of used files
formula_file_path = formula_file_path # molecule data
transform_file_path = transform_file_path # potential transformations


##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name): 
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name)
    print('done: create or replace database')

# establish connection to the new or replaced database based on 'db_name'
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# create molecule nodes in database
def create_nodes_molecule(call_graph, formula_file_path):
    graph = call_graph
    graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + formula_file_path + """' AS row
        //FIELDTERMINATOR ';'
        CREATE (:Molecule {
        //sample_id : row.measurement_id, 
        formula_string : row.formula_string,
        //formula_class : row.formula_class,  
        peak_relint_tic: toFloat(row.peak_relint_tic),
        point_in_time: toInteger(row.timepoint),
        C : toInteger(row.C), 
        H : toInteger(row.H), 
        O : toInteger(row.O), 
        N : toInteger(row.N), 
        S : toInteger(row.S),
        //measurement_rank : toInteger(row.measurement_rank),
        OC : toFloat(row.O)/toFloat(row.C),
        HC : toFloat(row.H)/toFloat(row.C)
        })
    """)
    print('done: create Molecule nodes')

# create constraint formula_string in combination with point in time is unique
def create_contraint(call_graph):
    graph = call_graph
    graph.run("CREATE CONSTRAINT ON (m:Molecule) ASSERT (m.formula_string, m.point_in_time) IS NODE KEY")
    print('done: create unique formula_string constraint')

# create index on formula strings
def create_index(call_graph):
    graph = call_graph
    graph.run("CREATE INDEX FOR (m:Molecule) ON (m.formula_string)")
    print('done: create index on formula strings')

# create POTENTIAL TRANSFORMATION relationship
def create_relationship_potential_transformation(call_graph, transform_file_path):
    call_graph.run("""
        CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:///""" + transform_file_path + """' AS row RETURN row",
        "WITH row.new_formula AS r_new_formula, row.formula_string AS r_formula_string, row.tu_C AS tu_C, row.tu_H AS tu_H, row.tu_O AS tu_O, row.tu_N AS tu_N, row.tu_S AS tu_S, row.transformation_unit as transformation_unit
        MATCH (m:Molecule), (m2:Molecule)
        WHERE m.formula_string = r_new_formula AND m2.formula_string = r_formula_string AND m.point_in_time = m2.point_in_time -1
        CREATE (m)-[:POTENTIAL_TRANSFORMATION{C: toInteger(tu_C), H: toInteger(tu_H), O: toInteger(tu_O), N: toInteger(tu_N), S: toInteger(tu_S), tu_pot: transformation_unit}]->(m2)
        RETURN count(*)",
        {batchSize: 500})
    """)
    print('done: create POTENTIAL_TRANSFORMATION relationship')

# create SAME_AS relationship
def create_relationship_same_as(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule), (m2:Molecule)
        WHERE m2.formula_string = m1.formula_string AND m2.point_in_time = m1.point_in_time + 1
        CREATE (m1)-[:SAME_AS]->(m2)
    """)
    print('done: create SAME_AS relationship')

# create intensity_trend property
def create_property_intensity_trend(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WITH (m2.peak_relint_tic/m1.peak_relint_tic) as tendency, m1, m2, s
        SET s.intensity_trend = apoc.math.round(tendency, 3)
    """)
    print('done: create property intensity_trend')


# delete molecules without edges of type pot
def delete_molecules_wo_pot(call_graph):
    call_graph.run("""
        MATCH (m:Molecule)
        WHERE NOT EXISTS ((m)-[:POTENTIAL_TRANSFORMATION]->(:Molecule))
        AND NOT EXISTS ((:Molecule)-[:POTENTIAL_TRANSFORMATION]->(m))
        DETACH DELETE m
    """)

    print("done: delete molecules without edges of type pot")


##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
create_database(host, user, passwd, db_name)
call_graph = get_database_connection(host, user, passwd, db_name)

# create graph
create_nodes_molecule(call_graph, formula_file_path)
create_contraint(call_graph)
create_index(call_graph)
create_relationship_potential_transformation(call_graph, transform_file_path)
create_relationship_same_as(call_graph)
create_property_intensity_trend(call_graph)
delete_molecules_wo_pot(call_graph)