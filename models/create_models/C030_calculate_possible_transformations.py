# Name: Philipp Plamper
# Date: 18. June 2021

from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_parallel
from C000_path_variables_create import int_change_path, path_prefix, written_transformations_file_path
from C000_path_variables_create import lower_limit, upper_limit
import pandas as pd


##################################################################################
#configure settings###############################################################
##################################################################################

# establish connection 
host = host
user = user
passwd = passwd

# select database name
db_name = db_name_parallel


##################################################################################
#calculations#####################################################################
##################################################################################

# set threshold
# describes what intensity trend is needed to be considered as increasing
upper_limit = upper_limit
# describes what intensity trend is needed to be considered as descreasing
lower_limit = lower_limit

# initiate connection
calc_transformations = Graph(host, auth=(user, passwd), name=db_name)

# set path
int_change_path = int_change_path


def incr_int():
    # calculate possible transformations of molecule with increasing intensity
    # problem if not every molecule exists in every measurement, creates gaps
    # -> don't know how to handle (decreasing or not existing)
    incr_int_df = calc_transformations.run("""
        MATCH (t1:Measurement)-[:MEASURED_IN]-(m1:Molecule)-[s:SAME_AS]-(m2:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE s.intensity_trend > """ + str(upper_limit) + """ AND t1.point_in_time = t2.point_in_time - 1
        WITH m2, t1, t2, s
        MATCH (t1)-[:MEASURED_IN]-(m3:Molecule)-[:POTENTIAL_TRANSFORMATION]-(m2)
        WITH m3, m2, t1, t2, s
        MATCH (t1)-[:MEASURED_IN]-(m3)-[s2:SAME_AS]-(:Molecule)-[:MEASURED_IN]-(t2)
        WHERE s2.intensity_trend < """ + str(lower_limit) + """
        WITH m2.C - m3.C as C, m2.H - m3.H as H, m2.O - m3.O as O, m2.N - m3.N as N, m2.S - m3.S as S, m2, m3, t1, t2, s, s2
        RETURN m2.formula_string as to_molecule, t1.sample_id as from_mid, t2.sample_id as to_mid, m3.formula_string as from_molecule, 
        C, H, O, N, S, s2.tendency_weight as tendency_weight_lose, s.tendency_weight as tendency_weight_gain,
        s2.tendency_weight_conn as tendency_weight_lose_conn, s.tendency_weight_conn as tendency_weight_gain_conn
    """).to_data_frame()
    # print(incr_int_df)
    # export dataframe
    incr_int_df.to_csv(int_change_path, sep=',', encoding='utf-8', index=False)
    print('done: get possible transformations')


# create strings of transformation unit
def calc_func_groups():
    data = pd.read_csv(int_change_path)
    tu_list = []

    #for index, row in data.iterrows():
    for row in data.itertuples(): # index=False
        tu_string = ""

        if row.C < 0: tu_string = "-" + tu_string + "C" + str(abs(row.C)) + " "
        elif row.C > 0: tu_string = tu_string + "C" + str(row.C) + " "
        else: tu_string

        if row.H < 0: tu_string = tu_string + "-H" + str(abs(row.H)) + " "
        elif row.H > 0: tu_string = tu_string + "H" + str(row.H) + " "
        else: tu_string

        if row.O < 0: tu_string = tu_string + "-O" + str(abs(row.O)) + " "
        elif row.O > 0: tu_string = tu_string + "O" + str(row.O) + " "
        else: tu_string

        if row.N < 0: tu_string = tu_string + "-N" + str(abs(row.N)) + " "
        elif row.N > 0: tu_string = tu_string + "N" + str(row.N) + " "
        else: tu_string

        if row.S < 0: tu_string = tu_string + "-S" + str(abs(row.S)) + " "
        elif row.S > 0: tu_string = tu_string + "S" + str(row.S) + " "
        else: tu_string

        # print(tu_string)
        tu_string = tu_string.rstrip()
        tu_list.append(tu_string)
    
    data['transformation_unit'] = tu_list
    data.to_csv(int_change_path, sep=',', encoding='utf-8', index=False)
    # print(data.head())
    print('done: calculate transformation unit names')


# optional: remove not relevant transformations ##################################

def remove_not_relevant():
    calc_df = pd.read_csv(int_change_path)
    given_data = pd.read_csv(written_transformations_file_path)

    for row in given_data.itertuples():
        if row.plus == 0:
            drop_data = calc_df[(calc_df['C'] == row.C) & (calc_df['H'] == row.H) & (calc_df['O'] == row.O) & (calc_df['N'] == row.N) & (calc_df['S'] == row.S)].index
            calc_df.drop(drop_data, inplace=True)
        if row.minus == 0:
            drop_data = calc_df[(calc_df['C'] == row.C*-1) & (calc_df['H'] == row.H*-1) & (calc_df['O'] == row.O*-1) & (calc_df['N'] == row.N*-1) & (calc_df['S'] == row.S*-1)].index
            calc_df.drop(drop_data, inplace=True)
    
    calc_df.to_csv(int_change_path, sep=',', encoding='utf-8', index=False)
    print('done: remove not relevant transformations')


# calc combined weight
def calc_weights():
    data = pd.read_csv(int_change_path)    
    
    conn_weight_list = []
    comb_weight_list = []

    for row in data.itertuples():
        comb_erg = (row.tendency_weight_lose + row.tendency_weight_gain)
        conn_erg = (row.tendency_weight_lose_conn + row.tendency_weight_gain_conn)
        
        comb_weight_list.append(comb_erg)
        conn_weight_list.append(conn_erg)
        
    data['weight_combined'] = comb_weight_list
    data['weight_connected'] = conn_weight_list
    data.to_csv(int_change_path, sep=',', encoding='utf-8', index=False)

    print('done: calculate weights of relationships')

# create relationship HAS_TRANSFORMED_INTO between transforming nodes over time
def create_temporal_transformations():
    calc_transformations.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + int_change_path + """' AS row
        MATCH (m1:Molecule), (m2:Molecule)
        WHERE m1.formula_string = row.from_molecule
        AND m1.sample_id = row.from_mid
        AND m2.formula_string = row.to_molecule
        AND m2.sample_id = row.to_mid
        CREATE (m1)-[:HAS_TRANSFORMED_INTO {C: toInteger(row.C), H: toInteger(row.H), O: toInteger(row.O), N: toInteger(row.N), S: toInteger(row.S), transformation_unit: row.transformation_unit, combined_weight: toFloat(row.weight_combined), connected_weight: toFloat(row.weight_connected)}]->(m2)
    """)
    print('done: creating HAS_TRANSFORMED_INTO Relationship')

# normalize outgoing hti transformations
def normalize_weights():
    calc_transformations.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(m:Molecule)
        WITH m.formula_string as fs, m.sample_id as mid, sum(t.connected_weight) as sum_weight
        MATCH (:Molecule)-[t1:HAS_TRANSFORMED_INTO]->(m1:Molecule)
        WHERE m1.formula_string = fs AND m1.sample_id = mid
        SET t1.normalized_connected_weight = apoc.math.round(t1.connected_weight/sum_weight, 3)
        RETURN fs, mid, sum_weight
    """)

    calc_transformations.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(m:Molecule)
        WITH m.formula_string as fs, m.sample_id as mid, sum(t.combined_weight) as sum_weight
        MATCH (:Molecule)-[t1:HAS_TRANSFORMED_INTO]->(m1:Molecule)
        WHERE m1.formula_string = fs AND m1.sample_id = mid
        SET t1.normalized_combined_weight = apoc.math.round(t1.combined_weight/sum_weight, 3)
        RETURN fs, mid, sum_weight
    """)
    print('done: normalize weights')

# call functions
incr_int()
calc_func_groups()
#remove_not_relevant() # probably redundant
calc_weights()
create_temporal_transformations()
normalize_weights()