# Name: Philipp Plamper 
# Date: 13. october 2021

import matplotlib.pyplot as plt
import numpy as np
from py2neo import Graph
import pandas as pd
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
#analyze functions################################################################
##################################################################################

def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection

# distribution of the intensity trends per measurement (increasing, decreasing, constant)
def get_intensity_trend_distribution(call_graph, export_path):
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
    plt.suptitle('Verteilung der Intensitätstrends an den ausgehenden "SAME_AS"-Kanten pro Messpunkt')
    plt.bar(same_rel.time, inc_rel.increase + dec_rel.decrease + same_rel.same, color = 'purple')
    plt.bar(dec_rel.time, dec_rel.decrease + inc_rel.increase, color = 'orange')
    plt.bar(inc_rel.time, inc_rel.increase, color = 'green')
    plt.plot(get_mol.time, get_mol.cmol, color = 'red')
    plt.xlabel('Messpunkt')
    plt.ylabel('Anzahl an ausgehenden \n "SAME_AS"-Kanten')
    plt.legend(['Anzahl Molekülknoten', 'gleichbleibende Intensität', 'sinkende Intensität', 'steigende Intensität'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(np.arange(0, len(get_mol), 1))

    name = 'graph_intensity_trend_distribution'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    print('done: create image "intensity trend distribution"')
    # plt.show()

# outgoing transformations per measurement
def outgoing_transformations_measurement(call_graph, export_path):
    or_cti = call_graph.run("""
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

    plt.suptitle('Ausgehende Transformationskanten je Messpunkt')
    plt.xlabel('Messpunkt')
    plt.ylabel('Anzahl ausgehende \n Transformationskanten')
    plt.bar(or_cti.time, or_cti.relationships_out, color='green')
    plt.bar(or_hti.time, or_hti.relationships_out, color='orange')
    plt.plot(get_mol.time, get_mol.cmol, color = 'black', lw=1.5)
    plt.legend(['Anzahl Molekülknoten', 'PT-Kanten', 'HTI-Kanten'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(np.arange(0, len(get_mol), 1))

    name = 'graph_outgoing_transformations_measurement'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    print('done: create image "outgoing transformations measurement"')
    # plt.show()

# occurrence oft outgoing transformations
def outgoing_transformations_occurrence(call_graph, export_path):
    most_outgoing_relationships = call_graph.run("""
        MATCH (m:Molecule)-[c:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN m.formula_string as formula_string, m.sample_id as mid, count(c) as rel_out
        //RETURN m.formula_string as formula_string, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame() 

    mor_cti = call_graph.run("""
        MATCH (m:Molecule)-[c:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN m.formula_string as formula_string, m.sample_id as mid, count(c) as rel_out
        //RETURN m.formula_string as formula_string, count(c) as rel_out
        ORDER BY count(c) DESC
    """).to_data_frame()

    af = {'formula_string':'count'}
    mor = most_outgoing_relationships.groupby(most_outgoing_relationships['rel_out'], as_index=False).aggregate(af)
    mor['hti_perc'] = mor.formula_string/mor.formula_string.sum()*100

    af_cti = {'formula_string':'count'}
    mor_cti = mor_cti.groupby(mor_cti['rel_out'], as_index=False).aggregate(af_cti)
    mor_cti['cti_perc'] = mor_cti.formula_string/mor_cti.formula_string.sum()*100

    plt.figure(figsize=(9, 3))
    plt.subplot(1, 2, 1)
    plt.suptitle('Verteilung der Anzahl der ausgehenden Transformationskanten pro Molekülknoten')
    plt.bar(mor_cti.rel_out, mor_cti.cti_perc, color='green')
    plt.xlabel('Anzahl ausgehende PT-Kanten')
    plt.ylabel('Anteil der Molekülknoten (%)')
    plt.xticks(np.arange(1, len(mor_cti)+1, 1))

    plt.subplot(1, 2, 2)
    plt.bar(mor.rel_out, mor.hti_perc, color='green')
    plt.xlabel('Anzahl ausgehende HTI-Kanten')
    plt.ylabel('Anteil der Molekülknoten (%)')
    plt.xticks(np.arange(1, len(mor)+1, 1))

    plt.tight_layout()

    name = 'graph_outgoing_transformations_occurrence'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    print('done: create image "outgoing transformations occurrence"')
    # plt.show()

# most occuring transformations overall
def most_occurring_transformations(call_graph, export_path):
    transform_count_hti = call_graph.run("""
    MATCH ()-[t:HAS_TRANSFORMED_INTO]->()
    RETURN t.transformation_unit as funktionelle_Gruppe, count(t.transformation_unit) as Anzahl_HTI_Kanten
    ORDER BY Anzahl_HTI_Kanten DESC
    """).to_data_frame()

    transform_count_cti = call_graph.run("""
    MATCH ()-[t:POTENTIAL_TRANSFORMATION]->()
    RETURN t.tu_pt as funktionelle_Gruppe, count(t.tu_pt) as Anzahl_CTI_Kanten
    ORDER BY Anzahl_CTI_Kanten DESC
    """).to_data_frame()

    df_join = pd.merge(transform_count_hti, transform_count_cti, on=["funktionelle_Gruppe"])
    df_join['share_hti'] = df_join.Anzahl_HTI_Kanten/df_join.Anzahl_HTI_Kanten.sum()*100
    df_join['share_cti'] = df_join.Anzahl_CTI_Kanten/df_join.Anzahl_CTI_Kanten.sum()*100

    labels = df_join['funktionelle_Gruppe'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, df_join.share_cti, height = 0.3, color='green')
    plt.barh(x - height/2 , df_join.share_hti, height = 0.3, color='orange')
    plt.yticks(x, labels = labels)
    plt.title('Anteil der chemischen Transformationen an Transformationskanten über alle Messpunkte')
    plt.ylabel('chemische Transformation')
    plt.xlabel('Anteil an Transformationskanten (%)')
    plt.legend(['PT-Kanten', 'HTI-Kanten'])

    name = 'graph_most_occurring_transformations'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    print('done: create image "most occurring transformations"')
    # plt.show()

# most occurring transformations per measurement
def most_occurring_transformations_measurement(call_graph, export_path):
    df_time = call_graph.run("""
        MATCH (t:Measurement)
        RETURN t.point_in_time as time
    """).to_data_frame()

    time_list = df_time['time'].to_list()
    del time_list[-1]

    df_tu_hti = call_graph.run("""
        MATCH (:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        RETURN DISTINCT t.transformation_unit as funktionelle_Gruppe
        """).to_data_frame()

    df_tu_pt = call_graph.run("""
        MATCH (:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        RETURN DISTINCT t.tu_pt as funktionelle_Gruppe
        """).to_data_frame()

    for ele in time_list:
        transform_count_hti = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:HAS_TRANSFORMED_INTO]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.transformation_unit as funktionelle_Gruppe, count(t.transformation_unit) as Anzahl_HTI_Kanten_""" + str(ele) + """
        ORDER BY Anzahl_HTI_Kanten_""" + str(ele) + """ DESC
        """).to_data_frame()

        transform_count_cti = call_graph.run("""
        MATCH (m:Measurement)-[:MEASURED_IN]-(:Molecule)-[t:POTENTIAL_TRANSFORMATION]->(:Molecule)
        WHERE m.point_in_time = """ + str(ele) + """
        RETURN t.tu_pt as funktionelle_Gruppe, count(t.tu_pt) as Anzahl_CTI_Kanten_""" + str(ele) + """
        ORDER BY Anzahl_CTI_Kanten_""" + str(ele) + """ DESC
        """).to_data_frame()
        
        df_tu_hti = pd.merge(df_tu_hti, transform_count_hti, on=["funktionelle_Gruppe"])
        df_tu_hti['share_hti_' + str(ele)] = df_tu_hti['Anzahl_HTI_Kanten_' + str(ele)]/df_tu_hti['Anzahl_HTI_Kanten_' + str(ele)].sum()*100
        
        df_tu_pt = pd.merge(df_tu_pt, transform_count_cti, on=["funktionelle_Gruppe"])
        df_tu_pt['share_cti_' + str(ele)] = df_tu_pt['Anzahl_CTI_Kanten_' + str(ele)]/df_tu_pt['Anzahl_CTI_Kanten_' + str(ele)].sum()*100

    df_join = pd.merge(df_tu_hti, df_tu_pt, on=["funktionelle_Gruppe"])

    for ele in time_list:
        element = 'share_hti_' + str(ele)
        df_join = df_join.sort_values([element])
        
        plt.figure()
        labels = df_join['funktionelle_Gruppe'].to_list()
        x = np.arange(len(labels))
        height = 0.3
        plt.figure(figsize=(4, 7))
        plt.barh(x + height/2, df_join['share_cti_' + str(ele)], height = 0.3, color='green')
        plt.barh(x - height/2 , df_join['share_hti_' + str(ele)], height = 0.3, color='orange')
        plt.yticks(x, labels = labels)
        plt.title('Anteil der chemischen Transformationen an Transformationskanten zu Messpunkt ' + str(ele))
        plt.ylabel('chemische Transformation')
        plt.xlabel('Anteil an Transformationskanten (%)')
        plt.legend(['PT-Kanten', 'HTI-Kanten'])

    name = 'graph_outgoing_transformations_occurrence_per_measurement'
    #plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    plt.close()
    print('done: create image "outgoing transformations occurrence per measurement"')
    # plt.show()

# average weight of transformations
def average_weight_transformations(call_graph, export_path):
    tch = call_graph.run("""
    MATCH ()-[t:HAS_TRANSFORMED_INTO]->()
    RETURN t.transformation_unit as funktionelle_Gruppe, 
            count(t.transformation_unit) as Anzahl_HTI_Kanten,
            avg(t.normalized_combined_weight) as avg_combined,
            avg(t.normalized_connected_weight) as avg_connect
    ORDER BY Anzahl_HTI_Kanten DESC
    """).to_data_frame()

    tch.avg_combined = tch.avg_combined
    tch.avg_connect = tch.avg_connect

    labels = tch['funktionelle_Gruppe'].to_list()
    x = np.arange(len(labels))
    height = 0.3
    plt.figure(figsize=(4, 7))
    plt.barh(x + height/2, tch.avg_combined, height = 0.3, color='green', label='CTI-Kanten')
    plt.barh(x - height/2 , tch.avg_connect, height = 0.3, color='orange', label='HTI-Kanten')
    plt.yticks(x, labels = labels)
    plt.title('Durchschnittliches Gewicht der chemischen Transformationen')
    plt.ylabel('chemische Transformation')
    plt.xlabel('Durchschnittliches Kantengewicht')
    plt.legend(['normalisiertes verbundenes Kantengewicht', 'normalisiertes kombiniertes Kantengewicht'], bbox_to_anchor=(1, 1))

    name = 'graph_average_weight_transformation'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    plt.clf()
    print('done: create image "average weight transformation"')
    # plt.show()


##################################################################################
#call functions###################################################################
##################################################################################

# establish database connection
call_graph = get_database_connection(host, user, passwd, db_name)

# set export path
export_path = path_prefix

# functions
get_intensity_trend_distribution(call_graph, export_path)
outgoing_transformations_measurement(call_graph, export_path)
outgoing_transformations_occurrence(call_graph, export_path)
most_occurring_transformations(call_graph, export_path)
most_occurring_transformations_measurement(call_graph, export_path)
average_weight_transformations(call_graph, export_path)
