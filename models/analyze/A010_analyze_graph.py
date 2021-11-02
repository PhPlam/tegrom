# Name: Philipp Plamper 
# Date: 02. november 2021

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from py2neo import Graph
from A000_path_variables_analyze import host, user, passwd, db_name_parallel
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
db_name = db_name_parallel


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
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend >= 1.025
        RETURN t.point_in_time as time, count(s) as increase
    """).to_data_frame()

    dec_rel = call_graph.run("""
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE s.intensity_trend <= 0.975
        RETURN t.point_in_time as time, count(s) as decrease
    """).to_data_frame()

    same_rel = call_graph.run("""
        MATCH (t:Measurement)-[:MEASURED_IN]-(m:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WHERE 0.975 < s.intensity_trend < 1.025
        RETURN t.point_in_time as time, count(s) as same
    """).to_data_frame()

    get_mol = call_graph.run("""
        MATCH (m:Molecule)-[]-(t:Measurement)
        WHERE t.point_in_time < 13
        RETURN t.point_in_time as time, count(m) as cmol
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
    or_pt = call_graph.run("""
        MATCH (t1:Measurement)-[:MEASURED_IN]-(:Molecule)-[c:POTENTIAL_TRANSFORMATION]->(:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE t2.point_in_time = t1.point_in_time + 1
        RETURN t1.point_in_time as time, count(c) as relationships_out
    """).to_data_frame()

    or_hti = call_graph.run("""
        MATCH (t1:Measurement)-[:MEASURED_IN]-(:Molecule)-[c:HAS_TRANSFORMED_INTO]->(:Molecule)-[:MEASURED_IN]-(t2:Measurement)
        WHERE t2.point_in_time = t1.point_in_time + 1
        RETURN t1.point_in_time as time, count(c) as relationships_out
    """).to_data_frame()

    get_mol = call_graph.run("""
        MATCH (m:Molecule)-[]-(t:Measurement)
        WHERE t.point_in_time < 13
        RETURN t.point_in_time as time, count(m) as cmol
    """).to_data_frame()

    plt.figure(figsize=(6, 3))

    plt.suptitle('Outgoing transformations per measurement')
    plt.xlabel('Measurement')
    plt.ylabel('Number of outgoing \n transformations')
    plt.bar(or_pt.time, or_pt.relationships_out, color='green')
    plt.bar(or_hti.time, or_hti.relationships_out, color='orange')
    plt.plot(get_mol.time, get_mol.cmol, color = 'black', lw=1.5)
    plt.legend(['Number of nodes "Molecule"', '"POTENTIAL_TRANSFORMATION" relationships', '"HAS_TRANSFORMED_INTO" relationships'], loc='upper left', bbox_to_anchor=(1, 1))
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
        MATCH (m:Molecule)-[c:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN m.formula_string as formula_string, m.sample_id as mid, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame() 

    mor_pt = call_graph.run("""
        MATCH (m:Molecule)-[c:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN m.formula_string as formula_string, m.sample_id as mid, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame()

    af = {'formula_string':'count'}
    mor = most_outgoing_relationships.groupby(most_outgoing_relationships['rel_out'], as_index=False).aggregate(af)
    mor['hti_perc'] = mor.formula_string/mor.formula_string.sum()*100

    af_pt = {'formula_string':'count'}
    mor_pt = mor_pt.groupby(mor_pt['rel_out'], as_index=False).aggregate(af_pt)
    mor_pt['pt_perc'] = mor_pt.formula_string/mor_pt.formula_string.sum()*100

    plt.figure(figsize=(9, 3))
    plt.subplot(1, 2, 1)
    plt.suptitle('Distribution of the number of outgoing transformations per node "Molecule"')
    plt.bar(mor_pt.rel_out, mor_pt.pt_perc, color='green')
    plt.xlabel('Number of outgoing \n "POTENTIAL_TRANSFORMATION" relationships')
    plt.ylabel('Proportion of nodes \n "Molecule" (%)')
    plt.xticks(np.arange(1, len(mor_pt)+1, 1))

    plt.subplot(1, 2, 2)
    plt.bar(mor.rel_out, mor.hti_perc, color='green')
    plt.xlabel('Number of outgoing \n "HAS_TRANSFORMED_INTO" relationships')
    plt.ylabel('Proportion of nodes \n "Molecule" (%)')
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
    transform_count_hti = call_graph.run("""
    MATCH ()-[t:HAS_TRANSFORMED_INTO]->()
    RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as count_HTI
    ORDER BY count_HTI DESC
    """).to_data_frame()

    transform_count_pt = call_graph.run("""
    MATCH ()-[t:POTENTIAL_TRANSFORMATION]->()
    RETURN t.tu_pt as transformation_unit, count(t.tu_pt) as count_PT
    ORDER BY count_PT DESC
    """).to_data_frame()

    df_join = pd.merge(transform_count_hti, transform_count_pt, on=["transformation_unit"])
    df_join['proportion_hti'] = df_join.count_HTI/df_join.count_HTI.sum()*100
    df_join['proportion_pt'] = df_join.count_PT/df_join.count_PT.sum()*100

    labels = df_join['transformation_unit'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, df_join.proportion_pt, height = 0.3, color='green')
    plt.barh(x - height/2 , df_join.proportion_hti, height = 0.3, color='orange')
    plt.yticks(x, labels = labels)
    plt.title('Proportion of chemical transformations across all measurements')
    plt.ylabel('Chemical transformation')
    plt.xlabel('Proportion of transformation (%)')
    plt.legend(['"POTENTIAL_TRANSFORMATION" relationships', '"HAS_TRANSFORMED_INTO" relationships'], loc='upper left', bbox_to_anchor=(1, 1))

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
        MATCH (t:Measurement)
        RETURN t.point_in_time as time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_hti = call_graph.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    df_tu_pt = call_graph.run("""
        MATCH (:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.tu_pt as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        transform_count_hti = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as count_HTI_""" + str(ele) + """
        ORDER BY count_HTI_""" + str(ele) + """ DESC
        """).to_data_frame()

        transform_count_pt = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.tu_pt as transformation_unit, count(t.tu_pt) as count_PT_""" + str(ele) + """
        ORDER BY count_PT_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu_hti = pd.merge(df_tu_hti, transform_count_hti, on=["transformation_unit"])
        df_tu_hti['proportion_hti_' + str(ele)] = df_tu_hti['count_HTI_' + str(ele)]/df_tu_hti['count_HTI_' + str(ele)].sum()*100
        
        df_tu_pt = pd.merge(df_tu_pt, transform_count_pt, on=["transformation_unit"])
        df_tu_pt['proportion_pt_' + str(ele)] = df_tu_pt['count_PT_' + str(ele)]/df_tu_pt['count_PT_' + str(ele)].sum()*100

    df_join = pd.merge(df_tu_hti, df_tu_pt, on=["transformation_unit"])

    for ele in time_list:
        element = 'proportion_hti_' + str(ele)
        df_join = df_join.sort_values([element])
        
        plt.figure()
        labels = df_join['transformation_unit'].to_list()
        x = np.arange(len(labels))
        height = 0.3
        plt.figure(figsize=(4, 7))
        plt.barh(x + height/2, df_join['proportion_pt_' + str(ele)], height = 0.3, color='green')
        plt.barh(x - height/2 , df_join['proportion_hti_' + str(ele)], height = 0.3, color='orange')
        plt.yticks(x, labels = labels)
        plt.title('Proportion of chemical transformations at measurement ' + str(ele))
        plt.ylabel('Chemical transformation')
        plt.xlabel('Proportion of transformation (%)')
        plt.legend(['"POTENTIAL_TRANSFORMATION" relationships', '"HAS_TRANSFORMED_INTO" relationships'])

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
        MATCH (t:Measurement)
        RETURN t.point_in_time as time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_hti = call_graph.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    df_tu_pt = call_graph.run("""
        MATCH (:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.tu_pt as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        transform_count_hti = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, count(t.transformation_unit) as Count_HTI_""" + str(ele) + """
        ORDER BY Count_HTI_""" + str(ele) + """ DESC
        """).to_data_frame()

        transform_count_pt = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.tu_pt as transformation_unit, count(t.tu_pt) as Count_PT_""" + str(ele) + """
        ORDER BY Count_PT_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu_hti = pd.merge(df_tu_hti, transform_count_hti, on=["transformation_unit"])
        df_tu_hti['proportion_hti_' + str(ele)] = df_tu_hti['Count_HTI_' + str(ele)]/df_tu_hti['Count_HTI_' + str(ele)].sum()*100
        
        df_tu_pt = pd.merge(df_tu_pt, transform_count_pt, on=["transformation_unit"])
        df_tu_pt['proportion_pt_' + str(ele)] = df_tu_pt['Count_PT_' + str(ele)]/df_tu_pt['Count_PT_' + str(ele)].sum()*100

    # drop columns 'Count_'
    # HTI
    droplist_hti = [i for i in df_tu_hti.columns if i.startswith('Count')]
    df_tu_hti = df_tu_hti.drop(columns=droplist_hti, axis=1)
    # PT
    droplist_pt = [i for i in df_tu_pt.columns if i.startswith('Count')]
    df_tu_pt = df_tu_pt.drop(columns=droplist_pt, axis=1)

    # make dataframe vertical
    # HTI
    df_tu_hti = df_tu_hti.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='proportion').drop('level_1',1)
    # PT
    df_tu_pt = df_tu_pt.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='proportion').drop('level_1',1)

    # add time to dataframe
    # HTI
    times_repeat = len(df_tu_hti)/len(time_list)
    times_list_hti = time_list * int(times_repeat)
    df_tu_hti['point_in_time'] = times_list_hti
    # PT
    times_repeat = len(df_tu_pt)/len(time_list)
    times_list_pt = time_list * int(times_repeat)
    df_tu_pt['point_in_time'] = times_list_pt

    # create plots
    # HTI
    fig = px.line(df_tu_hti, x='point_in_time', y='proportion', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "proportion": "proportion in %",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their proportion per measurement <br>-HAS_TRANSFORMED_INTO-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    # fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_most_occurring_transformations_measurement_line_hti.png")

    if export_html == 1:
        fig.write_html(export_path + "graph_most_occurring_transformations_measurement_line_hti.html")

    # PT
    fig = px.line(df_tu_pt, x='point_in_time', y='proportion', color='transformation_unit', symbol="transformation_unit",
                    labels={
                        "proportion": "proportion in %",
                        "point_in_time": "measurement"
                    },
                    title="Transformations and their proportion per measurement <br>-POTENTIAL_TRANSFORMATION-")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1
        )
    )
    # fig.show()

    if export_png == 1:
        fig.write_image(export_path + "graph_most_occurring_transformations_measurement_line_pt.png")

    if export_html == 1:
        fig.write_html(export_path + "graph_most_occurring_transformations_measurement_line_pt.html")

    print('done: create image "most occurring transformations measurement line hti and pt"')

# average weight of transformations all measurements one bar plot
def average_weight_transformations_bar(call_graph, export_png, export_path):
    tch = call_graph.run("""
    MATCH ()-[t:HAS_TRANSFORMED_INTO]->()
    RETURN t.transformation_unit as transformation_unit, 
            count(t.transformation_unit) as count_HTI,
            avg(t.normalized_combined_weight) as avg_combined,
            avg(t.normalized_connected_weight) as avg_connect
    ORDER BY count_HTI DESC
    """).to_data_frame()

    tch.avg_combined = tch.avg_combined
    tch.avg_connect = tch.avg_connect

    labels = tch['transformation_unit'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, tch.avg_combined, height = 0.3, color='green', label='PT-Kanten')
    plt.barh(x - height/2 , tch.avg_connect, height = 0.3, color='orange', label='HTI-Kanten')
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
        MATCH (t:Measurement)
        RETURN t.point_in_time as time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu = call_graph.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as transformation_unit
        """).to_data_frame()

    for ele in time_list:
        tch = call_graph.run("""
        MATCH (m:Measurement)-[]-(:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as transformation_unit, 
                count(t.transformation_unit) as Count_HTI_""" + str(ele) + """,
                avg(t.normalized_combined_weight) as avg_combined_""" + str(ele) + """,
                avg(t.normalized_connected_weight) as avg_connect_""" + str(ele) + """
        ORDER BY Count_HTI_""" + str(ele) + """ DESC
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

##################################################################################
#call functions###################################################################
##################################################################################

# establish database connection
call_graph = get_database_connection(host, user, passwd, db_name)

# set export
export_png = 1
export_html = 1
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
