# Name: Philipp Plamper 
# Date: 16. february 2021

import pandas as pd
from py2neo import Graph
from A000_path_variables_analyze import host, user, passwd, db_name_compact
from A000_path_variables_analyze import path_prefix

import warnings
warnings.filterwarnings("ignore")

##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name = db_name_compact


##################################################################################
#analyze functions################################################################
##################################################################################

def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

def create_graph_catalog(call_graph):

    for trans_count in range(1,13):

        call_graph.run("""
            CALL gds.graph.create.cypher(
            'graph_transition_""" + str(trans_count) + """',
            'MATCH (m:Molecule) RETURN id(m) AS id',
            'MATCH (m:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(m2:Molecule) 
                WHERE c.transition_""" + str(trans_count) + """[5] = 1 
                RETURN id(m) AS source, id(m2) AS target'
            )
        """)

def calc_pagerank_per_graph(call_graph):

    for trans_count in range(1,13):

        call_graph.run("""
            CALL gds.pageRank.write('graph_transition_""" + str(trans_count) + """', {
                maxIterations: 20,
                dampingFactor: 0.85,
                writeProperty: 'pagerank_trans_""" + str(trans_count) + """'
            })
        """)

##################################################################################
#call functions###################################################################
##################################################################################

# establish connection to graph
call_graph = get_database_connection(host, user, passwd, db_name)

create_graph_catalog(call_graph)
calc_pagerank_per_graph(call_graph)