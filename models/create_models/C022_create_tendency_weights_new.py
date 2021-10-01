# Name: Philipp Plamper
# Date: 12. may 2021

from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_parallel
from C000_path_variables_create import lower_limit, upper_limit
from C000_path_variables_create import tendency_weight_path
import pandas as pd

pd.options.mode.chained_assignment = None

##################################################################################
#configure settings###############################################################
##################################################################################

# establish connection 
host = host
user = user
passwd = passwd

# select database name
db_name = db_name_parallel

# path to file
tendency_weight_path = tendency_weight_path

##################################################################################
#calculate weights################################################################
##################################################################################

# create db connection
call_db = Graph(host, auth=(user, passwd), name=db_name)

# cypher query to get property intensity_trend from SAME_AS relationships
def get_tendencies():
    tendencies = call_db.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        RETURN m1.formula_string AS from_formula, m1.sample_id AS from_mid, m2.formula_string AS to_formula, m2.sample_id AS to_mid, s.intensity_trend as intensity_trend, m1.peak_relint_tic as int
        ORDER BY intensity_trend ASC
    """).to_data_frame()
    return tendencies

lower_limit = lower_limit
upper_limit = upper_limit

def new_calc_weight(tendencies):
    MAX = tendencies.intensity_trend.max()
    MIN = tendencies.intensity_trend.min()

    tendency_weight_list = []
    connect_weight_list = []

    for row in tendencies.itertuples():
        if row.intensity_trend >= upper_limit:
            res = row.intensity_trend/MAX
            tendency_weight_list.append(res)
            connect_weight_list.append(res * row.int)
        elif row.intensity_trend <= lower_limit:
            res = (1-row.intensity_trend)/(1-MIN)
            tendency_weight_list.append(res)
            connect_weight_list.append(res * row.int)
        else:
            tendency_weight_list.append(0) 
            connect_weight_list.append(0)

    tendencies['tendency_weight'] = tendency_weight_list
    tendencies['tendency_weight_conn'] = connect_weight_list

    tendencies.to_csv(tendency_weight_path, sep=',', encoding='utf-8', index=False)


# add weight property to Neo4j graph 
def add_weights_to_graph(tendency_weight_path):
    call_db.run("""
        LOAD CSV WITH HEADERS FROM 'file:///""" + tendency_weight_path + """' AS row
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE m1.formula_string = row.from_formula AND m1.sample_id = row.from_mid
	    AND m2.formula_string = row.to_formula AND m2.sample_id = row.to_mid
        SET s.tendency_weight = row.tendency_weight
        SET s.tendency_weight_conn = row.tendency_weight_conn
    """)
    print('done: creating tendency_weight property')

# call functions
tendencies = get_tendencies()
calculate_tendency_weights = new_calc_weight(tendencies)
add_weights_to_graph(tendency_weight_path)

########################################################################
########################################################################
########################################################################

# deprecated
# calculate specific weight of intensity trends
def calculate_weight(tendencies):

    # split and order dataframe
    tendencies_lower = tendencies[tendencies['intensity_trend'] <= 0.975]
    tendencies_upper = tendencies[tendencies['intensity_trend'] >= 1.025]
    tendencies_equal = tendencies[tendencies['intensity_trend'] < 1.025]
    tendencies_equal = tendencies_equal[tendencies_equal['intensity_trend'] > 0.975]

    # upper limit calculation
    #upper_limit = upper_limit
    percent = 1.025
    percent_factor = 0.025
    weight = 0.02
    increase_weight = 0.0103
    border = upper_limit*percent
    upper_weight_list = []

    for row in tendencies_upper.itertuples():
        if row.intensity_trend < border:
            upper_weight_list.append(weight*(row.int))
        else:
            percent = percent + percent_factor
            weight = weight + increase_weight
            border = upper_limit * percent        
            upper_weight_list.append(weight*(row.int))
    
    tendencies_upper['tendency_weight'] = upper_weight_list

    # lower limit calculation
    tendencies_lower = tendencies_lower.sort_values(by='intensity_trend', ascending=False)
    #lower_limit = lower_limit
    percent = 0.975 
    percent_factor = 0.025
    weight = 0.02
    increase_weight = 0.0272
    border = lower_limit*percent
    lower_weight_list = []

    for row in tendencies_lower.itertuples():
        if border < row.intensity_trend:
            lower_weight_list.append(weight*row.int)
        else:
            percent = percent - percent_factor
            weight = weight + increase_weight
            border = lower_limit * percent        
            lower_weight_list.append(weight*row.int)
        
    tendencies_lower['tendency_weight'] = lower_weight_list

    # equal calculation
    equal_weight_list = []

    for row in tendencies_equal.itertuples():
        equal_weight_list.append(0.0)

    tendencies_equal['tendency_weight'] = equal_weight_list

    # concat dataframes
    frames = [tendencies_upper, tendencies_lower, tendencies_equal]
    concat_df = pd.concat(frames)  

    # export as csv
    concat_df.to_csv(tendency_weight_path, sep=',', encoding='utf-8', index=False)  