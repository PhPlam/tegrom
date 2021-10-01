# Name: Philipp Plamper
# Date: 17. december 2020

from py2neo import Graph
import pandas as pd
import os

##################################################################################
#connection settings##############################################################

# host + port
host = 'http://localhost:11011'

# select database name
db_name = 'modelparallel'

# credentials for API
user = 'neo4j'
passwd = '1234'

# set path prefix to tmp files
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get path to files
path_prefix = str(abs_path[0]) + '/tmp_files/' # absolute path to used files


##################################################################################

model_graph = Graph(host, auth=(user, passwd), name=db_name)

# functional group * 12 
# = maximum number of times a functional group can be added to a molecule
# so once for each measurement

def cypher_iterative_prototype():
    # set transformation used to look up in in every measurement
    add_C = 0
    add_H = 2
    add_O = 1
    add_N = 0
    add_S = 0
    # timepoint 0 and 1 are essential, so script starts at timepoint 2
    timepoint = 2

    # script tested on model_compact
    # compare first two timepoints, where a possible transformation took place 
    # so molecules_2 = molecules_1 + transformation
    init_result = model_graph.run("""
        // timepoint 0 & 1
        MATCH (m:Molecule)-[:HAS_INTENSITY_AT]->(:Measurement {timepoint: 0}), (m2:Molecule)-[:HAS_INTENSITY_AT]->(:Measurement {timepoint: 1})
        WHERE m2.C = m.C + """ + str(add_C) + """ 
            AND m2.H = m.H + """ + str(add_H) + """ 
            AND m2.O = m.O + """ + str(add_O) + """
            AND m2.N = m.N + """ + str(add_N) + """
            AND m2.S = m.S + """ + str(add_S) + """
        RETURN m.formula_string AS m, m2.formula_string AS m2
    """).to_data_frame()

    print(init_result)
    # save result as temporary file
    init_result.to_csv(path_prefix + 'tmp.csv', sep=',', encoding='utf-8', index=False)
    data = init_result

    # compare for every timepoint 
    for x in range(timepoint, 13):
        print('####################################################')
        print('timepoint:', x)
        # mx = current timepoint
        mx = x
        # my = next timepoint
        my = x + 1
        print('mx:', mx)
        print('my:', my)
        try:
            # load temporary file and compare last saved timepoint with next one
            erg_tmp = model_graph.run("""
                LOAD CSV WITH HEADERS FROM 'file://""" + path_prefix + """tmp.csv' as row
                WITH row.m""" + str(mx) + """ AS m_tmp
                MATCH (m""" + str(mx) + """:Molecule {formula_string: m_tmp}), (m""" + str(my) + """:Molecule)-[:HAS_INTENSITY_AT]->(:Measurement {timepoint: """ + str(mx) + """})
                WHERE m""" + str(my) + """.C = m""" + str(mx) + """.C + """ + str(add_C) + """ 
                    AND m""" + str(my) + """.H = m""" + str(mx) + """.H + """ + str(add_H) + """ 
                    AND m""" + str(my) + """.O = m""" + str(mx) + """.O + """ + str(add_O) + """ 
                    AND m""" + str(my) + """.N = m""" + str(mx) + """.N + """ + str(add_N) + """ 
                    AND m""" + str(my) + """.S = m""" + str(mx) + """.S + """ + str(add_S) + """ 
                RETURN m""" + str(mx) + """.formula_string AS m""" + str(mx) + """, m""" + str(my) + """.formula_string AS m""" + str(my) + """
            """).to_data_frame()
            print(erg_tmp)
            # extend temporary file with new molecules
            data["m" + str(my)] = erg_tmp["m" + str(my)]
            data.to_csv(path_prefix + 'tmp.csv', sep=',', encoding='utf-8', index=False)
        except KeyError:
            pass
    
    # export final csv with all molecules of one transformation over all measurements
    export_name = 'C' + str(add_C) + 'H' + str(add_H) + 'O' + str(add_O) + 'N' + str(add_N) + 'S' + str(add_S)
    data.to_csv(path_prefix + 'final_' + export_name + '.csv', sep=',', encoding='utf-8', index=False)
    os.remove(path_prefix + 'tmp.csv')
    return 0

#cypher_iterative_prototype()

def test_incr_int():
    # calculate possible transformations of molecule with increasing intensity
    # problem if not every molecule exists in every measurement, creates gaps
    # -> don't know how to handle (decreasing or not existing)
    incr_int_df = model_graph.run("""
        MATCH (t1:Measurement)-[:MEASURED_IN]-(m1:Molecule)-[s:SAME_AS]-(m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE t1.timepoint = t2.timepoint - 1
        WITH m2, t1, t2, s
        MATCH (t1)-[:MEASURED_IN]-(m3:Molecule)-[:CAN_TRANSFORM_INTO]-(m2)
        WITH m3, m2, t1, t2, s
        MATCH (t1)-[:MEASURED_IN]-(m3)-[s2:SAME_AS]-(:Molecule)-[:MEASURED_IN]-(t2)
        WITH m2.C - m3.C as C, m2.H - m3.H as H, m2.O - m3.O as O, m2.N - m3.N as N, m2.S - m3.S as S, m2, m3, t1, t2, s, s2
        RETURN m2.formula_string as molecule, t1.measurement_id as from_mid, t2.measurement_id as to_mid, m3.formula_string as from_molecule, C, H, O, N, S, s2.tendency_weight as tendency_weight_lose, s.tendency_weight as tendency_weight_gain
    """).to_data_frame()
    print(incr_int_df)
    # export dataframe
    incr_int_df.to_csv("test.csv", sep=',', encoding='utf-8', index=False)
    print('done: get possible transformations')

# test_incr_int()

def test_calc_func_groups():
    data = pd.read_csv('/home/philipp/Desktop/test.csv')
    fg_list = []

    #for index, row in data.iterrows():
    for row in data.itertuples(): # index=False
        fg_string = ""

        if row.C < 0: fg_string = "-" + fg_string + "C" + str(abs(row.C)) + " "
        elif row.C > 0: fg_string = fg_string + "C" + str(row.C) + " "
        else: fg_string

        if row.H < 0: fg_string = fg_string + "-H" + str(abs(row.H)) + " "
        elif row.H > 0: fg_string = fg_string + "H" + str(row.H) + " "
        else: fg_string

        if row.O < 0: fg_string = fg_string + "-O" + str(abs(row.O)) + " "
        elif row.O > 0: fg_string = fg_string + "O" + str(row.O) + " "
        else: fg_string

        if row.N < 0: fg_string = fg_string + "-N" + str(abs(row.N)) + " "
        elif row.N > 0: fg_string = fg_string + "N" + str(row.N) + " "
        else: fg_string

        if row.S < 0: fg_string = fg_string + "-S" + str(abs(row.S)) + " "
        elif row.S > 0: fg_string = fg_string + "S" + str(row.S) + " "
        else: fg_string

        # print(fg_string)
        fg_string = fg_string.rstrip()
        fg_list.append(fg_string)
    
    data['fg_group'] = fg_list
    data.to_csv("test.csv", sep=',', encoding='utf-8', index=False)
    # print(data.head())
    print('done: calculate combined weight of relationship')

# test_calc_func_groups()

def test_calc_comb_weight():
    data = pd.read_csv('/home/philipp/Desktop/test.csv')
    # data contains tendency_weight_lose (1) and tendency_weight_gain (2)
    # (1) weight to describe how much intensity molecule lost between two timepoints
    # (2) weight to describe how much intensity the referring molecule gained
    
    helpList = []
    for row in data.itertuples():
        tmp_erg = (row.tendency_weight_lose + row.tendency_weight_gain)/2
        helpList.append(tmp_erg)
    
    data['tendency_weight_combined'] = helpList
    data.to_csv("test.csv", sep=',', encoding='utf-8', index=False)
    # print(data.head())

# test_calc_comb_weight()

def test_create_temporal_transformations():
    model_graph.run("""
        LOAD CSV WITH HEADERS FROM 'file:///home/philipp/Desktop/test.csv' AS row
        MATCH (m1:Molecule), (m2:Molecule)
        WHERE m1.formula_string = row.from_molecule
        AND m1.measurement_id = row.from_mid
        AND m2.formula_string = row.molecule
        AND m2.measurement_id = row.to_mid
        CREATE (m1)-[:COULD_TRANSFORMED_INTO {C: toInteger(row.C), H: toInteger(row.H), O: toInteger(row.O), N: toInteger(row.N), S: toInteger(row.S), functional_group: row.fg_group, combined_tendency_weight: toFloat(row.tendency_weight_combined)}]->(m2)
    """)
    print('done: creating HAS_TRANSFORMED_INTO Relationship')

# test_create_temporal_transformations()

def create_temporal_apoc():
    model_graph.run("""
        CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:///home/philipp/Desktop/test.csv' AS row RETURN row",
        "MATCH (m1:Molecule), (m2:Molecule)
            WHERE m1.formula_string = row.from_molecule
            AND m1.measurement_id = row.from_mid
            AND m2.formula_string = row.molecule
            AND m2.measurement_id = row.to_mid
            CREATE (m1)-[:COULD_TRANSFORMED_INTO {C: toInteger(row.C), H: toInteger(row.H), O: toInteger(row.O), N: toInteger(row.N), S: toInteger(row.S), functional_group: row.fg_group, combined_tendency_weight: toFloat(row.tendency_weight_combined)}]->(m2)
        RETURN count(*)",
        {batchSize: 500})
    """)
    print('done: creating CAN_TRANSFORM_INTO relationship')

create_temporal_apoc()