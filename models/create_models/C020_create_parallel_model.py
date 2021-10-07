# Name: Philipp Plamper 
# Date: 18. June 2021

# be sure your neo4j instance is up and running
# use neo4j import directory for files (else see next comment)
# for custom filepaths comment out 'dbms.directories.import=import' in neo4j conf

from py2neo import Graph
import os
from C000_path_variables_create import host, user, passwd, db_name_parallel
from C000_path_variables_create import formula_file_path, transform_file_path, measurement_file_path


##################################################################################
#configure settings###############################################################
##################################################################################

# establish connection 
host = host
user = user
passwd = passwd

# select database name
db_name = db_name_parallel

# filepaths
formula_file_path = formula_file_path
transform_file_path = transform_file_path
measurement_file_path = measurement_file_path

# create HAS_POSSIBLE_TRANSFORMATION
# 1 = yes, 0 = no
create_hpt = 0

##################################################################################
#create database##################################################################
##################################################################################

# new order for better performance ans simpler implementation
# only look at possible transformation at current and next timepoint
# differentiate between both by creating two different types of relationships

def new_create_transformations():
    # clean or create database
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name)

    # initiate connection
    create_graph = Graph(host, auth=(user, passwd), name=db_name)

    # create Molecule nodes
    create_graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + formula_file_path + """' AS row
        //FIELDTERMINATOR ';'
        CREATE (:Molecule {
        sample_id : row.measurement_id, 
        formula_string : row.formula_string,
        formula_class : row.formula_class,  
        peak_relint_tic: toFloat(row.peak_relint_tic),
        C : toInteger(row.C), 
        H : toInteger(row.H), 
        O : toInteger(row.O), 
        N : toInteger(row.N), 
        S : toInteger(row.S)
        })
    """)
    print('done: creating Molecule nodes')

    # create constraint formula_string in combination with sample_id is unique
    create_graph.run("CREATE CONSTRAINT ON (m:Molecule) ASSERT (m.formula_string, m.sample_id) IS NODE KEY")
    print('done: creating unique formula_string constraint')

    # create index on formula strings
    create_graph.run("CREATE INDEX FOR (m:Molecule) ON (m.formula_string)")
    print('done: creating index on formula strings')

    # create Measurement nodes
    create_graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + measurement_file_path + """' as row
        CREATE (:Measurement {
            sample_id: row.measurement_id,
            point_in_time: toInteger(row.timepoint)
            //radiation_dose: toFloat(row.radiation_dose),
            //time: row.time
            })
    """)
    print('done: creating Measurement nodes')

    # create MEASURED_IN relationship
    create_graph.run("""
        MATCH (m:Molecule), (t:Measurement)
        WHERE m.sample_id = t.sample_id
        CREATE (m)-[:MEASURED_IN]->(t)
    """)
    print('done: creating MEASURED_IN relationship')

    if create_hpt == 1:
        # create HAS_POSSIBLE_TRANSFORMATION (HPT) relationship
        create_graph.run("""
            CALL apoc.periodic.iterate(
            "LOAD CSV WITH HEADERS FROM 'file:///""" + transform_file_path + """' AS row RETURN row",
            "WITH row.new_formula AS r_new_formula, row.formula_string AS r_formula_string, row.tu_C AS tu_C, row.tu_H AS tu_H, row.tu_O AS tu_O, row.tu_N AS tu_N, row.tu_S AS tu_S
            MATCH (m:Molecule)-[:MEASURED_IN]-(t1:Measurement), (m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
            WHERE m.formula_string = r_new_formula AND m2.formula_string = r_formula_string AND t1.point_in_time = t2.point_in_time
            CREATE (m)-[:HAS_POSSIBLE_TRANSFORMATION {C: toInteger(tu_C), H: toInteger(tu_H), O: toInteger(tu_O), N: toInteger(tu_N), S: toInteger(tu_S)}]->(m2)
            RETURN count(*)",
            {batchSize: 500})
        """)
        print('done: creating HPT relationship')

    # create POTENTIAL TRANSFORMATION (PT) relationship
    create_graph.run("""
        CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:///""" + transform_file_path + """' AS row RETURN row",
        "WITH row.new_formula AS r_new_formula, row.formula_string AS r_formula_string, row.tu_C AS tu_C, row.tu_H AS tu_H, row.tu_O AS tu_O, row.tu_N AS tu_N, row.tu_S AS tu_S, row.transformation_unit as transformation_unit
        MATCH (m:Molecule)-[:MEASURED_IN]-(t1:Measurement), (m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE m.formula_string = r_new_formula AND m2.formula_string = r_formula_string AND t1.point_in_time = t2.point_in_time -1
        CREATE (m)-[:POTENTIAL_TRANSFORMATION{C: toInteger(tu_C), H: toInteger(tu_H), O: toInteger(tu_O), N: toInteger(tu_N), S: toInteger(tu_S), tu_pt: transformation_unit}]->(m2)
        RETURN count(*)",
        {batchSize: 500})
    """)
    print('done: creating PT relationship')

    # create SAME_AS relationship
    # probably a problem if same molecule miss out one measurement
    create_graph.run("""
        MATCH (m1:Molecule)-[:MEASURED_IN]-(t1:Measurement), (m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE m2.formula_string = m1.formula_string AND t2.point_in_time = t1.point_in_time + 1
        CREATE (m1)-[:SAME_AS]->(m2)
    """)
    print('done: creating SAME_AS relationship')

    # create intensity_trend property
    create_graph.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WITH (m2.peak_relint_tic/m1.peak_relint_tic) as tendency, m1, m2, s
        SET s.intensity_trend = apoc.math.round(tendency, 3)
    """)
    print('done: creating property intensity_trend')

new_create_transformations()