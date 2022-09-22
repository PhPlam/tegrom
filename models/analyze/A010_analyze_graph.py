# Name: Philipp Plamper 
# Date: 21. september 2022

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from py2neo import Graph
from scipy import stats
from A000_path_variables_analyze import host, user, passwd, db_name_temporal
from A000_path_variables_analyze import path_prefix, path_prefix_csv
import A001_parameters_analysis as pa

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
db_name = db_name_temporal


##################################################################################
#analyze functions################################################################
##################################################################################

def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# distribution of the intensity trends per measurement (increasing, decreasing, constant)
def intensity_trend_distribution(call_graph, export_png, export_path):
    inc_rel = call_graph.run("""
        MATCH (m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend >= 1.025
        RETURN m.point_in_time as time, count(s) as increase
    """).to_data_frame()

    dec_rel = call_graph.run("""
        MATCH (m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend <= 0.975
        RETURN m.point_in_time as time, count(s) as decrease
    """).to_data_frame()

    same_rel = call_graph.run("""
        MATCH (m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE 0.975 < s.intensity_trend < 1.025
        RETURN m.point_in_time as time, count(s) as same
    """).to_data_frame()

    get_mol = call_graph.run("""
        MATCH (m:Molecule)
        RETURN m.point_in_time as time, count(m) as cmol
        ORDER BY time ASC
    """).to_data_frame()

    inc_rel['mid'] = inc_rel.increase + dec_rel.decrease + same_rel.same

    plt.figure(figsize=(6, 3))
    plt.suptitle('Distribution of the intensity trends at "SAME_AS" relationships per measurement')
    plt.bar(same_rel.time, inc_rel.increase + dec_rel.decrease + same_rel.same, color = 'purple')
    plt.bar(dec_rel.time, dec_rel.decrease + inc_rel.increase, color = 'orange')
    plt.bar(inc_rel.time, inc_rel.increase, color = 'green')
    plt.plot(get_mol.time, get_mol.cmol, color = 'red')
    plt.xlabel('Measurement')
    plt.ylabel('Number of outgoing \n "SAME_AS" relationships')
    plt.legend(['Number nodes "Molecule"', 'Persistent intensity', 'Decreasing intensity', 'Inreasing intensity'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(np.arange(0, len(get_mol), 1))

    if export_png == 1:
        name = 'graph_intensity_trend_distribution'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "intensity trend distribution"')
    # plt.show()

# outgoing transformations per measurement
def outgoing_transformations_measurement(call_graph, export_png, export_path):
    or_pot = call_graph.run("""
        MATCH (m1:Molecule)-[c:POTENTIAL_TRANSFORMATION]->(m2:Molecule)
        WHERE m2.point_in_time = m1.point_in_time + 1
        RETURN m1.point_in_time as time, count(c) as relationships_out
    """).to_data_frame()

    or_prt = call_graph.run("""
        MATCH (m1:Molecule)-[c:PREDICTED_TRANSFORMATION]->(m2:Molecule)
        WHERE m2.point_in_time = m1.point_in_time + 1
        RETURN m1.point_in_time as time, count(c) as relationships_out
    """).to_data_frame()

    get_mol = call_graph.run("""
        MATCH (m:Molecule)
        RETURN m.point_in_time as time, count(m) as cmol
        ORDER BY time ASC
    """).to_data_frame()

    plt.figure(figsize=(6, 3))

    plt.suptitle('Outgoing transformations per measurement')
    plt.xlabel('Measurement')
    plt.ylabel('Number of outgoing \n transformations')
    plt.bar(or_pot.time, or_pot.relationships_out, color='green')
    plt.bar(or_prt.time, or_prt.relationships_out, color='orange')
    plt.plot(get_mol.time, get_mol.cmol, color = 'black', lw=1.5)
    plt.legend(['Number of nodes "Molecule"', '"POTENTIAL_TRANSFORMATION" relationships', '"PREDICTED_TRANSFORMATION" relationships'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(np.arange(0, len(get_mol), 1))

    if export_png == 1:
        name = 'graph_outgoing_transformations_measurement'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')
    
    plt.clf()
    print('done: create image "outgoing transformations measurement"')
    # plt.show()

# occurrence oft outgoing transformations
def outgoing_transformations_occurrence(call_graph, export_png, export_path):
    most_outgoing_relationships = call_graph.run("""
        MATCH (m:Molecule)-[c:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN m.formula_string as formula_string, m.point_in_time as pit, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame() 

    mor_pot = call_graph.run("""
        MATCH (m:Molecule)-[c:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN m.formula_string as formula_string, m.point_in_time as pit, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame()

    af = {'formula_string':'count'}
    mor = most_outgoing_relationships.groupby(most_outgoing_relationships['rel_out'], as_index=False).aggregate(af)
    mor['prt_perc'] = mor.formula_string/mor.formula_string.sum()*100

    af_pot = {'formula_string':'count'}
    mor_pot = mor_pot.groupby(mor_pot['rel_out'], as_index=False).aggregate(af_pot)
    mor_pot['pot_perc'] = mor_pot.formula_string/mor_pot.formula_string.sum()*100

    plt.figure(figsize=(9, 3))
    plt.subplot(1, 2, 1)
    plt.suptitle('Distribution of the number of outgoing transformations per node "Molecule"')
    plt.bar(mor_pot.rel_out, mor_pot.pot_perc, color='green')
    plt.xlabel('Number of outgoing \n "POTENTIAL_TRANSFORMATION" relationships')
    plt.ylabel('Share of nodes \n "Molecule" (%)')
    plt.xticks(np.arange(1, len(mor_pot)+1, 1))

    plt.subplot(1, 2, 2)
    plt.bar(mor.rel_out, mor.prt_perc, color='green')
    plt.xlabel('Number of outgoing \n "PREDICTED_TRANSFORMATION" relationships')
    plt.ylabel('Share of nodes \n "Molecule" (%)')
    plt.xticks(np.arange(1, len(mor)+1, 1))

    plt.tight_layout()

    if export_png == 1:
        name = 'graph_outgoing_transformations_occurrence'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "outgoing transformations occurrence"')
    # plt.show()

# most occuring transformations overall
def most_occurring_transformations(call_graph, export_png, export_path):
    transform_count_prt = call_graph.run("""
    MATCH ()-[t:PREDICTED_TRANSFORMATION]->()
    RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as count_prt
    ORDER BY count_prt DESC
    """).to_data_frame()

    transform_count_pot = call_graph.run("""
    MATCH ()-[t:POTENTIAL_TRANSFORMATION]->()
    RETURN t.tu_pot as transformation_unit, count(t.tu_pot) as count_pot
    ORDER BY count_pot DESC
    """).to_data_frame()

    df_join = pd.merge(transform_count_prt, transform_count_pot, on=["transformation_unit"])
    df_join['Share_prt'] = df_join.count_prt/df_join.count_prt.sum()*100
    df_join['Share_pot'] = df_join.count_pot/df_join.count_pot.sum()*100

    labels = df_join['transformation_unit'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, df_join.Share_pot, height = 0.3, color='green')
    plt.barh(x - height/2 , df_join.Share_prt, height = 0.3, color='orange')
    plt.yticks(x, labels = labels)
    plt.title('Share of chemical transformations across all measurements')
    plt.ylabel('Chemical transformation')
    plt.xlabel('Share of transformation (%)')
    plt.legend(['"POTENTIAL_TRANSFORMATION" relationships', '"PREDICTED_TRANSFORMATION" relationships'], loc='upper left', bbox_to_anchor=(1, 1))

    if export_png == 1:
        name = 'graph_most_occurring_transformations'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "most occurring transformations"')
    # plt.show()

# most occurring transformations all measurements several bar plots
# don't use
def most_occurring_transformations_measurement_bar(call_graph, export_png, export_path):
    df_time = call_graph.run("""
        MATCH (m:Molecule)
        RETURN DISTINCT m.point_in_time as time
        ORDER BY time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_prt = call_graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    df_tu_pot = call_graph.run("""
        MATCH (:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.tu_pot as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        transform_count_prt = call_graph.run("""
        MATCH (m:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as count_prt_""" + str(ele) + """
        ORDER BY count_prt_""" + str(ele) + """ DESC
        """).to_data_frame()

        transform_count_pot = call_graph.run("""
        MATCH (m:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.tu_pot as transformation_unit, count(t.tu_pot) as count_pot_""" + str(ele) + """
        ORDER BY count_pot_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu_prt = pd.merge(df_tu_prt, transform_count_prt, on=["transformation_unit"])
        df_tu_prt['Share_prt_' + str(ele)] = df_tu_prt['count_prt_' + str(ele)]/df_tu_prt['count_prt_' + str(ele)].sum()*100
        
        df_tu_pot = pd.merge(df_tu_pot, transform_count_pot, on=["transformation_unit"])
        df_tu_pot['Share_pot_' + str(ele)] = df_tu_pot['count_pot_' + str(ele)]/df_tu_pot['count_pot_' + str(ele)].sum()*100

    df_join = pd.merge(df_tu_prt, df_tu_pot, on=["transformation_unit"])

    for ele in time_list:
        element = 'Share_prt_' + str(ele)
        df_join = df_join.sort_values([element])
        
        plt.figure()
        labels = df_join['transformation_unit'].to_list()
        x = np.arange(len(labels))
        height = 0.3
        plt.figure(figsize=(4, 7))
        plt.barh(x + height/2, df_join['Share_pot_' + str(ele)], height = 0.3, color='green')
        plt.barh(x - height/2 , df_join['Share_prt_' + str(ele)], height = 0.3, color='orange')
        plt.yticks(x, labels = labels)
        plt.title('Share of chemical transformations at measurement ' + str(ele))
        plt.ylabel('Chemical transformation')
        plt.xlabel('Share of transformation (%)')
        plt.legend(['"POTENTIAL_TRANSFORMATION" relationships', '"PREDICTED_TRANSFORMATION" relationships'])

    if export_png == 1:
        name = 'graph_outgoing_transformations_occurrence_per_measurement'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    plt.close()
    print('done: create image "outgoing transformations occurrence per measurement"')
    # plt.show()

# most occurring transformations per measurement in line plot
def most_occurring_transformations_measurement_line(call_graph, export_png, export_html, export_path):
    df_time = call_graph.run("""
        MATCH (m:Molecule)
        RETURN DISTINCT m.point_in_time as time
        ORDER BY time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_prt = call_graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    df_tu_pot = call_graph.run("""
        MATCH (:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.tu_pot as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        transform_count_prt = call_graph.run("""
        MATCH (m:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as Count_prt_""" + str(ele) + """
        ORDER BY Count_prt_""" + str(ele) + """ DESC
        """).to_data_frame()

        transform_count_pot = call_graph.run("""
        MATCH (m:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.tu_pot as transformation_unit, count(t.tu_pot) as Count_pot_""" + str(ele) + """
        ORDER BY Count_pot_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu_prt = pd.merge(df_tu_prt, transform_count_prt, on=["transformation_unit"])
        df_tu_prt['Share_prt_' + str(ele)] = df_tu_prt['Count_prt_' + str(ele)]/df_tu_prt['Count_prt_' + str(ele)].sum()*100
        
        df_tu_pot = pd.merge(df_tu_pot, transform_count_pot, on=["transformation_unit"])
        df_tu_pot['Share_pot_' + str(ele)] = df_tu_pot['Count_pot_' + str(ele)]/df_tu_pot['Count_pot_' + str(ele)].sum()*100

    # drop columns 'Count_'
    # prt
    droplist_prt = [i for i in df_tu_prt.columns if i.startswith('Count')]
    df_tu_prt = df_tu_prt.drop(columns=droplist_prt, axis=1)
    # pot
    droplist_pot = [i for i in df_tu_pot.columns if i.startswith('Count')]
    df_tu_pot = df_tu_pot.drop(columns=droplist_pot, axis=1)

    # make dataframe vertical
    # prt
    df_tu_prt = df_tu_prt.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='Share').drop('level_1',1)
    # pot
    df_tu_pot = df_tu_pot.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='Share').drop('level_1',1)

    # add time to dataframe
    # prt
    times_repeat = len(df_tu_prt)/len(time_list)
    times_list_prt = time_list * int(times_repeat)
    df_tu_prt['point_in_time'] = times_list_prt
    # pot
    times_repeat = len(df_tu_pot)/len(time_list)
    times_list_pot = time_list * int(times_repeat)
    df_tu_pot['point_in_time'] = times_list_pot

    # create plots
    # prt
    fig = px.line(df_tu_prt, x='point_in_time', y='Share', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "Share": "Share in %",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their Share per measurement <br>-PREDICTED_TRANSFORMATION-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    # fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_most_occurring_transformations_measurement_line_prt.png")

    if export_html == 1:
        fig.write_html(export_path + "graph_most_occurring_transformations_measurement_line_prt.html")

    # pot
    fig = px.line(df_tu_pot, x='point_in_time', y='Share', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "Share": "Sheare in %",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their Share per measurement <br>-POTENTIAL_TRANSFORMATION-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    # fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_most_occurring_transformations_measurement_line_pot.png")

    if export_html == 1:
        fig.write_html(export_path + "graph_most_occurring_transformations_measurement_line_pot.html")

    print('done: create image "most occurring transformations measurement line prt and pot"')

# average weight of transformations all measurements one bar plot
def average_weight_transformations_bar(call_graph, export_png, export_path):
    tch = call_graph.run("""
    MATCH ()-[t:PREDICTED_TRANSFORMATION]->()
    RETURN t.transformation_unit as transformation_unit, 
            count(t.transformation_unit) as count_prt,
            avg(t.normalized_combined_weight) as avg_combined,
            avg(t.normalized_connected_weight) as avg_connect
    ORDER BY count_prt DESC
    """).to_data_frame()

    tch.avg_combined = tch.avg_combined
    tch.avg_connect = tch.avg_connect

    labels = tch['transformation_unit'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, tch.avg_combined, height = 0.3, color='green', label='pot-Kanten')
    plt.barh(x - height/2 , tch.avg_connect, height = 0.3, color='orange', label='prt-Kanten')
    plt.yticks(x, labels = labels)
    plt.title('Average weight of transformation')
    plt.ylabel('Chemical transformation')
    plt.xlabel('Average weight')
    plt.legend(['normalized connected weight', 'normalized combined weight'], bbox_to_anchor=(1, 1))

    if export_png == 1:
        name = 'graph_average_weight_transformations_bar'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "average weight transformations bar"')
    # plt.show()

# average weight of transformations per measurement in line plot
def average_weight_transformations_line(call_graph, export_png, export_html, export_path):
    df_time = call_graph.run("""
        MATCH (m:Molecule)
        RETURN DISTINCT m.point_in_time as time
        ORDER BY time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu = call_graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        tch = call_graph.run("""
        MATCH (m:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, 
                count(t.transformation_unit) as Count_prt_""" + str(ele) + """,
                avg(t.normalized_combined_weight) as avg_combined_""" + str(ele) + """,
                avg(t.normalized_connected_weight) as avg_connect_""" + str(ele) + """
        ORDER BY Count_prt_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu = pd.merge(df_tu, tch, on=["transformation_unit"])
        
    # drop columns 
    # for combined
    droplist_combined = [i for i in df_tu.columns if i.startswith('Count') or i.startswith('avg_connect')]
    df_tu_combined = df_tu.drop(columns=droplist_combined, axis=1)
    # for connected
    droplist_connected = [i for i in df_tu.columns if i.startswith('Count') or i.startswith('avg_combined')]
    df_tu_connected = df_tu.drop(columns=droplist_connected, axis=1)

    # make dataframe vertical
    # for combined
    df_tu_combined = df_tu_combined.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='average_weight').drop('level_1',1)
    # for connected
    df_tu_connected = df_tu_connected.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='average_weight').drop('level_1',1)

    # add time to dataframe
    # for combined
    times_repeat = len(df_tu_combined)/len(time_list)
    times_list_combined = time_list * int(times_repeat)
    df_tu_combined['point_in_time'] = times_list_combined
    # for connected
    times_repeat = len(df_tu_connected)/len(time_list)
    times_list_connected = time_list * int(times_repeat)
    df_tu_connected['point_in_time'] = times_list_connected

    # create plots
    # for combined
    fig = px.line(df_tu_combined, x='point_in_time', y='average_weight', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "average_weight": "average combined weight",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their weight per measurement <br>-combined weight-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    #fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_average_weight_transformations_line_combined.png")

    if export_html == 1:
        fig.write_html(export_path + "graph_average_weight_transformations_line_combined.html")

    # for connected
    fig = px.line(df_tu_connected, x='point_in_time', y='average_weight', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "average_weight": "average connected weight",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their weight per measurement <br>-connected weight-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    #fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_average_weight_transformations_line_connected.png")
    
    if export_html == 1:
        fig.write_html(export_path + "graph_average_weight_transformations_line_connected.html")
    
    print('done: create image "average weight transformations line combined and connected"')


# Prepare Dataframe with prts and tus
def prepare_prts_tu(call_graph):
    df_time = call_graph.run("""
        MATCH (m:Molecule)
        RETURN DISTINCT m.point_in_time as time
        ORDER BY time ASC
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_prt = call_graph.run("""
        MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        transform_count_prt = call_graph.run("""
        MATCH (m:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as Count_prt_""" + str(ele) + """
        ORDER BY Count_prt_""" + str(ele) + """ DESC
        """).to_data_frame()

        df_tu_prt = pd.merge(df_tu_prt, transform_count_prt, on=["transformation_unit"])
        df_tu_prt['proportion_prt_' + str(ele)] = df_tu_prt['Count_prt_' + str(ele)]/df_tu_prt['Count_prt_' + str(ele)].sum()*100
        
    # drop columns 'Count_'
    # prt
    droplist_prt = [i for i in df_tu_prt.columns if i.startswith('Count')]
    df_tu_prt = df_tu_prt.drop(columns=droplist_prt, axis=1)

    # make dataframe vertical
    # prt
    df_tu_prt = df_tu_prt.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='proportion').drop('level_1',1)

    # add time to dataframe
    # prt
    times_repeat = len(df_tu_prt)/len(time_list)
    times_list_prt = time_list * int(times_repeat)
    df_tu_prt['point_in_time'] = times_list_prt

    return df_tu_prt


# Different trends of transformation units
def trends_transformation_units(call_graph, df_tu_prt, export_png, export_path):
    tu = call_graph.run("""
        MATCH (:Molecule)-[h:PREDICTED_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT h.transformation_unit AS tu
    """).to_data_frame()

    tu_list = tu.tu.tolist()
    tu_dict_list = []

    for tu in tu_list:
        pick_tu = df_tu_prt[df_tu_prt.transformation_unit == tu]
        res = stats.linregress(pick_tu.point_in_time, pick_tu.proportion)
        increase = ((res.slope*11+res.intercept)/(res.intercept))-1
        
        tu_dict = {
            'tu': tu,
            'increase': increase,
            'share_mean_perc': pick_tu.proportion.mean()
        }
        tu_dict_list.append(tu_dict)
        
    df_tu = pd.DataFrame(tu_dict_list)
    df_tu = df_tu.sort_values(by=['increase'], ascending=False).reset_index(drop=True)
    df_tu['inc_perc'] = df_tu.increase*100

    # first plot
    fig = plt.figure(figsize=(12,4))
    plt.bar(df_tu.tu, df_tu.inc_perc)
    plt.xlabel('transformation unit', fontsize=12)
    plt.ylabel('increase in shares in %', fontsize=12)
    plt.title('transformation units and their increase in shares (from first to last measurement)', fontweight="bold")
    plt.xticks(rotation=45)
    plt.axhline(y=0, color='r', linestyle='-', label='no increase')
    plt.legend(loc='upper right')
    
    if export_png == 1:
        plt.savefig(export_path + 'transformation_units_increase_share.png', dpi=150 ,bbox_inches='tight')

    # second plot
    fig = plt.figure(figsize=(12,4))
    plt.bar(df_tu.tu, df_tu.share_mean_perc)
    plt.xlabel('transformation unit', fontsize=12)
    plt.ylabel('average share in %', fontsize=12)
    plt.title('transformation units and their average share', fontweight="bold")
    plt.xticks(rotation=45)
    plt.axhline(y=4.5, color='r', linestyle='-', label='average overall')
    plt.legend(loc='upper left')

    if export_png == 1:
        plt.savefig(export_path + 'transformation_units_average_share.png', dpi=150 ,bbox_inches='tight')

    print('done: create images "transformations units"')


# development of specific transformation units
def trend_single_tu(df_tu_prt, tu, tu_2, export_png, export_path):
    tu = tu
    pick_tu = df_tu_prt[df_tu_prt.transformation_unit == tu]
    res = stats.linregress(pick_tu.point_in_time, pick_tu.proportion)

    tu_2 = tu_2
    pick_tu_2 = df_tu_prt[df_tu_prt.transformation_unit == tu_2]
    res_2 = stats.linregress(pick_tu_2.point_in_time, pick_tu_2.proportion)

    fig = plt.figure(figsize=(12,4))
    plt.scatter(pick_tu.point_in_time, pick_tu.proportion, s=10, label=tu_2, c='r')
    plt.plot(pick_tu.point_in_time, res.intercept + res.slope*pick_tu.point_in_time, c='r')

    if tu_2 != tu:
        plt.scatter(pick_tu_2.point_in_time, pick_tu_2.proportion, s=10, label=tu, c='b')
        plt.plot(pick_tu_2.point_in_time, res_2.intercept + res_2.slope*pick_tu_2.point_in_time, c='b')
        
    plt.legend()
    plt.xlabel('measurement', fontsize=12)
    plt.ylabel('share in %', fontsize=12)
    plt.title('Development of share of transformation units', fontsize=12, fontweight='bold')
    plt.xticks(np.arange(min(pick_tu.point_in_time), max(pick_tu.point_in_time)+1, 1.0))

    if export_png == 1:
        plt.savefig(export_path + 'occurence_development_single_tu.png', dpi=150 ,bbox_inches='tight')

    print('done: create image "single transformation unit trend"')


# transform string of transformation unit to format of string in graph
def calculate_tu_string(ele, direction):
    tu_string = ""
    
    C = ele.C if direction == 'plus' else ele.C*(-1)
    H = ele.H if direction == 'plus' else ele.H*(-1)
    O = ele.O if direction == 'plus' else ele.O*(-1)
    N = ele.N if direction == 'plus' else ele.N*(-1)
    S = ele.S if direction == 'plus' else ele.S*(-1)

    if C < 0: tu_string = "-" + tu_string + "C" + str(abs(C)) + " "
    elif C > 0: tu_string = tu_string + "C" + str(C) + " "
    else: tu_string

    if H < 0: tu_string = tu_string + "-H" + str(abs(H)) + " "
    elif H > 0: tu_string = tu_string + "H" + str(H) + " "
    else: tu_string

    if O < 0: tu_string = tu_string + "-O" + str(abs(O)) + " "
    elif O > 0: tu_string = tu_string + "O" + str(O) + " "
    else: tu_string

    if N < 0: tu_string = tu_string + "-N" + str(abs(N)) + " "
    elif N > 0: tu_string = tu_string + "N" + str(N) + " "
    else: tu_string

    if S < 0: tu_string = tu_string + "-S" + str(abs(S)) + " "
    elif S > 0: tu_string = tu_string + "S" + str(S) + " "
    else: tu_string
        
    tu_string = tu_string.rstrip()
        
    return tu_string


# trend of photo products and photo degraded components
def trend_products_degraded(df_tu, call_graph, export_png, export_path):
    # calculate strings of transformation units
    tu_list_plus = []
    tu_list_minus = []
    for ele in df_tu.itertuples():
        
        if ele.plus == 1:
            direction = 'plus'
            tu_string_plus = calculate_tu_string(ele, direction)
            tu_list_plus.append(tu_string_plus)
            
        if ele.minus == 1:
            direction = 'minus'
            tu_string_minus = calculate_tu_string(ele, direction)
            tu_list_minus.append(tu_string_minus)

    # get data from graph
    df_photo_prod = call_graph.run("""
        MATCH (m:Molecule)-[h:PREDICTED_TRANSFORMATION]->(:Molecule)
        WHERE h.transformation_unit IN """ + str(tu_list_plus) + """
        RETURN m.point_in_time as pit, count(h) as cnt_prt_prod
    """).to_data_frame()

    df_photo_degr = call_graph.run("""
    MATCH (m:Molecule)-[h:PREDICTED_TRANSFORMATION]->(:Molecule)
    WHERE h.transformation_unit IN """ + str(tu_list_minus) + """
    RETURN m.point_in_time as pit, count(h) as cnt_prt_degr
    """).to_data_frame()

    df_merge_prod_degr = pd.merge(df_photo_prod, df_photo_degr, on=["pit"])

    # normalization because photo degradation and photo addition have different occurrence
    df_merge_prod_degr['cnt_prt_prod_norm'] = df_merge_prod_degr.cnt_prt_prod/len(tu_list_plus)
    df_merge_prod_degr['cnt_prt_degr_norm'] = df_merge_prod_degr.cnt_prt_degr/len(tu_list_minus)
    df_merge_prod_degr['cnt_prt_prod_share'] = df_merge_prod_degr.cnt_prt_prod/(df_merge_prod_degr.cnt_prt_prod+df_merge_prod_degr.cnt_prt_degr)
    df_merge_prod_degr['cnt_prt_degr_share'] = df_merge_prod_degr.cnt_prt_degr/(df_merge_prod_degr.cnt_prt_prod+df_merge_prod_degr.cnt_prt_degr)
    df_merge_prod_degr['cnt_prt_prod_norm_share'] = df_merge_prod_degr.cnt_prt_prod_norm/(df_merge_prod_degr.cnt_prt_prod_norm+df_merge_prod_degr.cnt_prt_degr_norm)
    df_merge_prod_degr['cnt_prt_degr_norm_share'] = df_merge_prod_degr.cnt_prt_degr_norm/(df_merge_prod_degr.cnt_prt_prod_norm+df_merge_prod_degr.cnt_prt_degr_norm)

    # create plots
    fig = plt.figure(figsize=(15,5))
    plt.suptitle('Different approaches to show trend of photo products and photo degraded components', fontsize=14, fontweight="bold")

    plt.subplot(1,2,1)
    plt.plot(df_merge_prod_degr.pit, df_merge_prod_degr.cnt_prt_prod_share, label='photo product', marker='o')
    plt.plot(df_merge_prod_degr.pit, df_merge_prod_degr.cnt_prt_degr_share, label='photo degraded', marker='o')
    plt.xlabel('measurement', fontsize=14)
    plt.ylabel('share in %', fontsize=14)
    plt.title('Measurement X share', fontweight="bold")
    plt.legend(loc='upper left')
    plt.xticks(np.arange(min(df_merge_prod_degr.pit), max(df_merge_prod_degr.pit)+1, 1.0))

    plt.subplot(1,2,2)
    plt.plot(df_merge_prod_degr.pit, df_merge_prod_degr.cnt_prt_prod_norm_share, label='photo product', marker='o')
    plt.plot(df_merge_prod_degr.pit, df_merge_prod_degr.cnt_prt_degr_norm_share, label='photo degraded', marker='o')
    plt.xlabel('measurement', fontsize=14)
    plt.ylabel('share of normalized in %', fontsize=14)
    plt.title('Measurement X share of normalized', fontweight="bold")
    plt.legend(loc='upper left')
    plt.xticks(np.arange(min(df_merge_prod_degr.pit), max(df_merge_prod_degr.pit)+1, 1.0))

    plt.tight_layout()

    if export_png == 1:
        plt.savefig(export_path + 'trend_of_product_degradation.png', dpi=150 ,bbox_inches='tight')

    print('done: create image "trend photo product and degradation"')

##################################################################################
#call functions###################################################################
##################################################################################

# establish database connection
call_graph = get_database_connection(host, user, passwd, db_name)

# set export
export_png = 1
export_html = 0
export_path = path_prefix

# functions
intensity_trend_distribution(call_graph, export_png, export_path)
outgoing_transformations_measurement(call_graph, export_png, export_path)
outgoing_transformations_occurrence(call_graph, export_png, export_path)
most_occurring_transformations(call_graph, export_png, export_path)
# most_occurring_transformations_measurement_bar(call_graph, 0, export_path)
most_occurring_transformations_measurement_line(call_graph, export_png, export_html, export_path)
average_weight_transformations_bar(call_graph, export_png, export_path)
average_weight_transformations_line(call_graph, export_png, export_html, export_path)

df_prts_tus = prepare_prts_tu(call_graph)
trends_transformation_units(call_graph, df_prts_tus, export_png, export_path)
trend_single_tu(df_prts_tus, pa.tu, pa.tu_2, export_png, export_path)

df_tu = pd.read_csv(path_prefix_csv + "/transformations_handwritten.csv")
trend_products_degraded(df_tu, call_graph, export_png, export_path)