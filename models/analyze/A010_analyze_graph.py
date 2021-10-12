# Name: Philipp Plamper 
# Date: 12. october 2021

import os
import matplotlib.pyplot as plt
import numpy as np
from py2neo import Graph
from matplotlib import rc
from numpy.polynomial.polynomial import polyfit
from A000_path_variables_analyze import host, user, passwd, db_name_parallel
from A000_path_variables_analyze import path_prefix


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name = db_name_parallel


##################################################################################
#create connection to database####################################################
##################################################################################

def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection


##################################################################################
#analyze##########################################################################
##################################################################################

# distribution of the intensity trends per measurement (increasing, decreasing, constant)
def get_intensity_trend_distribution(model_graph):
    inc_rel = model_graph.run("""
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend >= 1.025
        RETURN t.point_in_time as time, count(s) as increase
    """).to_data_frame()

    dec_rel = model_graph.run("""
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend <= 0.975
        RETURN t.point_in_time as time, count(s) as decrease
    """).to_data_frame()

    same_rel = model_graph.run("""
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE 0.975 < s.intensity_trend < 1.025
        RETURN t.point_in_time as time, count(s) as same
    """).to_data_frame()

    get_mol = model_graph.run("""
        MATCH (m:Molecule)-[]-(t:Measurement)
        WHERE t.point_in_time < 13
        RETURN t.point_in_time as time, count(m) as cmol
    """).to_data_frame()

    print(inc_rel.increase.mean())
    print(dec_rel.decrease.mean())
    print(same_rel.same.mean())
    inc_rel['mid'] = inc_rel.increase + dec_rel.decrease + same_rel.same
    print(inc_rel.mid.mean())
    print(get_mol.cmol.mean())

    plt.figure(figsize=(6, 3))
    plt.suptitle('Verteilung der Intensitätstrends an den ausgehenden "SAME_AS"-Kanten pro Messpunkt')
    #plt.bar(outgoing_relationships.time, outgoing_relationships.relationships_out)
    plt.bar(same_rel.time, inc_rel.increase + dec_rel.decrease + same_rel.same, color = 'purple')
    plt.bar(dec_rel.time, dec_rel.decrease + inc_rel.increase, color = 'orange')
    plt.bar(inc_rel.time, inc_rel.increase, color = 'green')
    plt.plot(get_mol.time, get_mol.cmol, color = 'red')
    plt.xlabel('Messpunkt')
    plt.ylabel('Anzahl an ausgehenden \n "SAME_AS"-Kanten')
    plt.legend(['Anzahl Molekülknoten', 'gleichbleibende Intensität', 'sinkende Intensität', 'steigende Intensität'], loc='upper left', bbox_to_anchor=(1, 1))
    x = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    plt.xticks(x)

    #specific = '000_a'
    #plt.savefig(path_file + specific + '.png', bbox_inches='tight')

    plt.show()


##################################################################################
#call functions###################################################################
##################################################################################

model_graph = get_database_connection(host, user, passwd, db_name)
get_intensity_trend_distribution(model_graph)