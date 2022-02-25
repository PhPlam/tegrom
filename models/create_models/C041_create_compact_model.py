# Name: Philipp Plamper 
# Date: 24. february 2022

import os
from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_parallel, db_name_compact
from C000_path_variables_create import unique_formulas_file_path, transform_file_path


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name_parallel = db_name_parallel
db_name_compact = db_name_compact

# path of used files
unique_formulas_file_path = unique_formulas_file_path # unique formula strings
transform_file_path = transform_file_path # potential transformations


##################################################################################
#set path for tmp files###########################################################
##################################################################################

# set relative filepath prefix
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0]) + '/files_tmp_compact/' # add path to files in project folder
path_prefix = path_prefix.replace('\\', '/') # necessary for application in Windows


##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name_compact): 
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name_compact)
    print('done: create or replace database')


# establish connection to the new or replaced database based on 'db_name'
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection


# deal with not existing "SAME_AS" relationships
# get all PT relationships
def get_relationships(call_graph):
    new_model_paths = call_graph.run("""
        MATCH (m1:Molecule)-[p:POTENTIAL_TRANSFORMATION]->(m2:Molecule)
        OPTIONAL MATCH (m1)-[s1:SAME_AS]->(:Molecule)
        OPTIONAL MATCH (:Molecule)-[s2:SAME_AS]->(m2)
        WHERE m2.point_in_time = m1.point_in_time + 1
        RETURN m1.formula_string as mol_from, m1.peak_relint_tic as mol_from_int, m1.point_in_time as mol_from_time, 
        s1.intensity_trend as mol_from_int_trend, m2.formula_string as mol_to, m2.peak_relint_tic as mol_to_int, 
        m2.point_in_time as mol_to_time, s2.intensity_trend as mol_to_int_trend, p.tu_pt as transformation_unit 
    """).to_data_frame()

    # fill null values of columns matched with 'Optional Match'
    new_model_paths = new_model_paths.fillna(0)

    ### Pfade
    # export
    #new_model_paths.to_csv('new_model_transitions/full_paths.csv', sep=',', encoding='utf-8', index=False)
    print('done: get all potential transformation relationships')

    return new_model_paths


# create molecule nodes from unique formula strings
def create_nodes_molecule(call_graph):
    call_graph.run("""
    LOAD CSV WITH HEADERS FROM 'file:///""" + unique_formulas_file_path + """' as row
    CREATE (:Molecule {formula_string:row.formula_string,         
            C : toInteger(row.C), 
            H : toInteger(row.H), 
            O : toInteger(row.O), 
            N : toInteger(row.N), 
            S : toInteger(row.S),
            formula_class : row.formula_class,
            OC : toFloat(row.O)/toFloat(row.C),
            HC : toFloat(row.H)/toFloat(row.C)})
    RETURN count(*)
    """)

    print('done: create nodes molecule')


# create index on formula string
def create_index(call_graph):
    call_graph.run("CREATE INDEX FOR (m:Molecule) ON (m.formula_string)")

    print('done: create index on formula string')


# create CHEMICAL_TRANSFORMATION relationship
def create_relationship_chemical_transformation(call_graph):
    call_graph.run("""
        USING PERIODIC COMMIT 1000
        LOAD CSV WITH HEADERS FROM 'file:///""" + transform_file_path + """' as row
        MATCH (m1:Molecule), (m2:Molecule)
        WHERE m1.formula_string = row.new_formula 
            AND m2.formula_string = row.formula_string
        CREATE (m1)-[:CHEMICAL_TRANSFORMATION {tu:row.transformation_unit}]->(m2)
        RETURN count(*)
    """)

    print('done: create relationship chemical transformation')


# create and set properties at relationship CHEMICAL_TRANSRFORMATION
def set_properties_chemical_transformation(call_graph, new_model_paths):
    for i in range (1,new_model_paths.mol_to_time.max()+1):
        is_hti_list = []
        new_model_paths_trim = new_model_paths[new_model_paths.mol_to_time == i]
        
        for row in new_model_paths_trim.itertuples():
            if 0 < row.mol_from_int_trend < 0.975 and row.mol_to_int_trend > 1.025:
                is_hti_list.append(1)
            else:
                is_hti_list.append(0)
        new_model_paths_trim['is_hti'] = is_hti_list
        
        new_model_paths_trim.to_csv(path_prefix + 'paths' + str(i) + '.csv', sep=',', encoding='utf-8', index=False)
        
        call_graph.run("""
            LOAD CSV WITH HEADERS FROM 'file:///""" + path_prefix + """paths""" + str(i) +""".csv' as row
            MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(m2:Molecule)
            WHERE m1.formula_string = row.mol_from
                AND m2.formula_string = row.mol_to
                AND c.tu = row.transformation_unit
            SET c.transition_""" + str(i) + """ = [toFloat(row.mol_to_time), toFloat(row.mol_from_int), 
                toFloat(row.mol_to_int), toFloat(row.mol_from_int_trend), 
                toFloat(row.mol_to_int_trend), toFloat(row.is_hti)]
        """)
    
    print('done: set properties at relationship chemical transformation')
        
    # order of properties in List
    # 1. transition
    # 2. relative intensity of source molecule
    # 3. relative intensity of target molecule
    # 4. intensity trend to molecule with same formula of source molecule
    # 5. intensity trend from molecule with same formula of target molecule
    # 6. is hti, see RelIdent-algorithm


# delete [:CT] with possible transformation but without existing transition
# transformation is theoretical possible but molecules are too far away 
# e.g. first measurement and last measurement
def delete_without_properties(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
        WITH m1, c, size(keys(c)) as keys
        WHERE keys <= 1 
        DETACH DELETE c
        RETURN count(c)
    """)

    print('done: delete relationships without properties')


# property 'transition_count'
# = number of transtions between two molecules 
def create_property_transition_count(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
        WITH m1, c, size(keys(c))-1 as keys
        SET c.transition_count = keys
        RETURN m1.formula_string, keys LIMIT 5
    """)

    print('done: create property transition count')


# property 'hti_count'
# = number of transtions recognizes as edge of type 'hti' 
def create_property_hti_count(call_graph, new_model_paths):
    call_graph.run("""
        MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
        SET c.hti_count = 0
        RETURN count(*)
    """)

    for i in range(1,new_model_paths.mol_to_time.max()+1):
        call_graph.run("""
            MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
            WHERE c.transition_""" + str(i) + """[5] = 1
            SET c.hti_count = c.hti_count + 1
            RETURN count(*)
        """)

    print('done: create property hti count')


##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
create_database(host, user, passwd, db_name_compact)


# connect to parallel model
call_graph = get_database_connection(host, user, passwd, db_name_parallel)
new_model_paths = get_relationships(call_graph)


# connect to compact model
call_graph = get_database_connection(host, user, passwd, db_name_compact)
create_nodes_molecule(call_graph)
create_index(call_graph)
create_relationship_chemical_transformation(call_graph)
set_properties_chemical_transformation(call_graph, new_model_paths)
delete_without_properties(call_graph)
create_property_transition_count(call_graph)
create_property_hti_count(call_graph, new_model_paths)
