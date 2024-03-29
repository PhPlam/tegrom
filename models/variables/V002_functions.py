# Name: Philipp Plamper 
# Date: 24. march 2023

import os
import pandas as pd
import numpy as np
from scipy import stats
from neo4j import GraphDatabase

### functions to ###
### provide functionality ###

# establish connection to the new or replaced database based on 'db_name'
def connect_to_database(host, user, passwd, db_name):
    # credentials
    URI = host
    AUTH = (user, passwd)
    DB = db_name
    # create connection and open session
    driver = GraphDatabase.driver(URI, auth=AUTH, database=DB)
    session = driver.session()
    print('done: establish connection to database ' + db_name)
    return session


### functions for ###
### graph analysis ###

def graph_get_time(session, query_params):
    df_time = session.run(
        "MATCH (m:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "RETURN count(m) as count_nodes, "
            "m." + query_params['prop_node_snapshot'] + " as property_time, "
            "m." + query_params['prop_extra_12'] + " as radiation_dose "
        "ORDER BY property_time ASC"
    ).to_df()

    # property "radiation_dose" does not exist if it is not a photolysis experiment
    try:
        radiation = df_time['radiation_dose'].to_list()
        radiation_diff = ['NULL'] + ['+' + str(round(x - radiation[i - 1], 1)) for i, x in enumerate(radiation)][1:]
        df_time['rad_diff'] = radiation_diff
    except Exception:
        pass

    print('done: get all time sequences')
    return df_time

def graph_get_member_intensity_trend(session, query_params, lower, upper, trend):
    df_member_trend = session.run(
        "MATCH (m:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[s:" + query_params['label_same_as'] + "]->(m2:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "WHERE " + str(lower) + " <= s." + query_params['prop_edge_value_2'] + " <= " + str(upper) + " "
        "RETURN m." + query_params['prop_node_snapshot'] + "+1 as property_time, "
            "count(s) as " + trend + " "
        "ORDER BY property_time ASC"
    ).to_df()

    print('done: get member of trend: ' + trend)
    return df_member_trend

def graph_get_transformations(session, edge_type, query_params):
    df_transformations = session.run(
        "MATCH (m1:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[c:" + edge_type + "]->(m2:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
        "RETURN m1." + query_params['prop_node_snapshot'] + "+1 as property_time, "
            "count(c) as count_relationships"
    ).to_df()

    print('done: get transformations: ' + edge_type)
    return df_transformations

# get transformation units and their share per snapshot
def get_share_transformation_units(session, query_params, transition_property):
    df_time = graph_get_time(session, query_params)
    time_list = df_time['property_time'].to_list()
    del time_list[-1]

    # get transformations units and their count for every snapshot
    df_transformation_unit_count = pd.DataFrame()
    for ele in time_list:
        count_predicted = session.run(
            "MATCH (:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[t:" + query_params['label_predicted_edge'] + "]->(:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
            "WITH DISTINCT t." + query_params['prop_edge_value_1'] + " as transformation_unit "
            "OPTIONAL MATCH (m:" + query_params['label_node'] + query_params['nodes_temporal'] + ")-[t:" + query_params['label_predicted_edge'] + "]->(:" + query_params['label_node'] + query_params['nodes_temporal'] + ") "
            "WHERE t." + query_params['prop_edge_value_1'] + " = transformation_unit "
                "AND m." + query_params['prop_node_snapshot'] + "  = " + str(ele) + " "
            "RETURN transformation_unit as transformation_unit, " 
                "t." + query_params['prop_extra_13'] + " as is_addition, "
                "count(t." + query_params['prop_edge_value_1'] + ") as count_prt_" + str(ele) + ", "
                "avg(t." + query_params['prop_extra_15'] + ")*100 as weight_prt_" + str(ele) + ""
        ).to_df()
        
        if df_transformation_unit_count.empty:
            df_transformation_unit_count = count_predicted.copy()
        else:
            df_transformation_unit_count  = pd.merge(df_transformation_unit_count, count_predicted[['transformation_unit', 'count_prt_'+str(ele), 'weight_prt_'+str(ele)]], on=["transformation_unit"])

        # calculate share of transformation units in every snapshot
        df_transformation_unit_count['transition_' + str(ele+1)] = df_transformation_unit_count['count_prt_' + str(ele)]/df_transformation_unit_count['count_prt_' + str(ele)].sum()*100

    # drop columns start with 'Count_'
    droplist_columns = [i for i in  df_transformation_unit_count.columns if i.startswith('count')]
    df_transformation_unit_count =  df_transformation_unit_count.drop(columns=droplist_columns, axis=1)

    if transition_property == 'weight':
        droplist_columns = [i for i in  df_transformation_unit_count.columns if i.startswith('transition')]
        df_transformation_unit_count =  df_transformation_unit_count.drop(columns=droplist_columns, axis=1)
    elif transition_property == 'share':
        droplist_columns = [i for i in  df_transformation_unit_count.columns if i.startswith('weight')]
        df_transformation_unit_count =  df_transformation_unit_count.drop(columns=droplist_columns, axis=1)

    df_transformation_unit_count = df_transformation_unit_count.fillna(0)

    print('done: get all ' + query_params['prop_edge_value_1'] + ' and their share per ' + query_params['prop_node_snapshot'])
    return df_transformation_unit_count

# calculate increase of transformation unit
# type = 'average' -> steepness of slope = average increase
# type = 'total' -> increase from first to last measurement on slope (distance) = total increase
# 'total' formula -> percentage increase = (final value - starting value)/|starting value| * 100
# e.g. https://www.omnicalculator.com/math/percentage-increase 
def calculate_increase(df_transformation_unit_count, df_time, type):
    time_list = df_time['property_time'].to_list()
    del time_list[-1]

    transformation_unit_dict_list = []
    for tu in df_transformation_unit_count.transformation_unit:
        pick_tu = df_transformation_unit_count[df_transformation_unit_count.transformation_unit == tu]
        values = pick_tu.iloc[0,2:].values.tolist()
        
        # calculate angle 
        res = stats.linregress(time_list, values)

        if type == 'average':
            # calculate average increase from angle of slope
            angle = np.rad2deg(np.arctan((res.slope*len(time_list))/(len(time_list))))
            increase = np.tan(angle*(np.pi/180))*100 
        elif type == 'total':
            increase = ((res.slope*(len(time_list)-1)+res.intercept) - (res.slope*time_list[0]+res.intercept)) / abs(res.slope*time_list[0]+res.intercept) * 100.0
        
        tu_dict = {
            'tu': tu,
            'is_addition': pick_tu.is_addition.values[0],
            'increase': increase,
            'mean_perc': np.mean(values)
        }
        transformation_unit_dict_list.append(tu_dict)
        

    df_transformation_unit = pd.DataFrame(transformation_unit_dict_list)
    df_transformation_unit = df_transformation_unit.sort_values(by=['increase'], ascending=False).reset_index(drop=True)

    print('done: calculate increase')
    return df_transformation_unit

# get properties of top five communities
# label propagation algorithm
def get_properties_top_communities(session, query_params, algorithm):
    properties_communities = session.run(
        "MATCH (m:" + query_params['label_node'] + query_params['nodes_light'] + ") "
        "WITH m.community_" + algorithm + " as community, count(*) as member, "
            "avg(m." + query_params['prop_extra_2'] + query_params['prop_extra_1'] + ") as avg_hc, "
            "avg(m." + query_params['prop_extra_4'] + query_params['prop_extra_1'] + ") as avg_oc "
        "ORDER BY member DESC "
        "LIMIT 5 "
        "OPTIONAL MATCH (m:" + query_params['label_node'] + query_params['nodes_light'] + ")-[ct:" + query_params['label_chemical_edge'] + "]->(m2:" + query_params['label_node'] + query_params['nodes_light'] + ") "
        "WHERE m.community_" + algorithm + " = community "
            "AND m2.community_" + algorithm + " = community "
        "RETURN community, member, avg_hc, avg_oc, "
            "sum(ct." + query_params['prop_extra_8'] + ") as sum_ct, "
            "sum(ct." + query_params['prop_extra_9'] + ") as sum_prt, "
            "avg(ct." + query_params['prop_extra_8'] + ") as avg_ct, "
            "avg(ct." + query_params['prop_extra_9'] + ") as avg_prt, "
            "avg(m." + query_params['prop_extra_18'] + ") as cnt_occ, "
            "avg(m." + query_params['prop_extra_17'] + ") as avg_int"
    ).to_df()

    print('done: get properties of top five communities')
    return properties_communities