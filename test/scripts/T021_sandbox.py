# Name: Philipp Plamper
# Date: 28. janaury 2021

from py2neo import Graph
import pandas as pd
import os

##################################################################################
#connection settings##############################################################

# host + port
host = 'http://localhost:11008'

# select database name
db_name = 'modelparallel'

# credentials for API
user = 'neo4j'
passwd = '1234'

model_graph = Graph(host, auth=(user, passwd), name=db_name)

##################################################################################

# fault tolerance MS
# considered as increasing intensity
upper_limit = 1.025
# considered as decreasing intensity
lower_limit = 0.975

def decr_int():
    # calculate molecules with decreasing intensities and their possible transformations
    decr_int_df = model_graph.run("""
        MATCH (t1:Measurement)-[:MEASURED_IN]-(m1:Molecule)-[s:SAME_AS]-(m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE s.intensity_trend < """ + str(lower_limit) + """ AND t1.timepoint = t2.timepoint - 1
        WITH m1, t1, t2
        MATCH (m1)-[:CAN_TRANSFORM_INTO]-(m3:Molecule)-[:MEASURED_IN]-(t2)
        WITH m3, m1, t1, t2
        MATCH (t2)-[:MEASURED_IN]-(m3)-[s2:SAME_AS]-(:Molecule)-[:MEASURED_IN]-(t1)
        WHERE s2.intensity_trend > """ + str(upper_limit) + """
        WITH m3.C - m1.C as C, m3.H - m1.H as H, m3.O - m1.O as O, m3.N - m1.N as N, m3.S - m1.S as S, m1, m3, t1, t2
        RETURN m1.formula_string as molecule, t1.measurement_id as from_mid, t2.measurement_id as to_mid, m3.formula_string as to_molecule, C, H, O, N, S
    """).to_data_frame()
    print(decr_int_df)
    # export dataframe
    decr_int_df.to_csv("test.csv", sep=',', encoding='utf-8', index=False)

decr_int()