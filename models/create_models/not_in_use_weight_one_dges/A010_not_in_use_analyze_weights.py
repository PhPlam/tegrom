# Name: Philipp Plamper
# Date: 11. november 2022


# average weight of transformations all measurements one bar plot
# def average_weight_transformations_bar(call_graph, export_png, export_path):
#     tch = call_graph.run("""
#     MATCH ()-[t:PREDICTED_TRANSFORMATION]->()
#     RETURN t.transformation_unit as transformation_unit, 
#             count(t.transformation_unit) as count_prt,
#             avg(t.normalized_combined_weight) as avg_combined,
#             avg(t.normalized_connected_weight) as avg_connect
#     ORDER BY count_prt DESC
#     """).to_data_frame()

#     tch.avg_combined = tch.avg_combined
#     tch.avg_connect = tch.avg_connect

#     labels = tch['transformation_unit'].to_list()
#     x = np.arange(len(labels))
#     height = 0.3
#     plt.figure(figsize=(4, 7))
#     plt.barh(x + height/2, tch.avg_combined, height = 0.3, color='green', label='pot-Kanten')
#     plt.barh(x - height/2 , tch.avg_connect, height = 0.3, color='orange', label='prt-Kanten')
#     plt.yticks(x, labels = labels)
#     plt.title('Average weight of transformation')
#     plt.ylabel('Chemical transformation')
#     plt.xlabel('Average weight')
#     plt.legend(['normalized connected weight', 'normalized combined weight'], bbox_to_anchor=(1, 1))

#     if export_png == 1:
#         name = 'graph_average_weight_transformations_bar'
#         plt.savefig(export_path + name + '.png', bbox_inches='tight')

#     plt.clf()
#     print('done: create image "average weight transformations bar"')
#     # plt.show()

# average weight of transformations per measurement in line plot
# def average_weight_transformations_line(call_graph, export_png, export_html, export_path):
#     df_time = call_graph.run("""
#         MATCH (m:Molecule)
#         RETURN DISTINCT m.point_in_time as time
#         ORDER BY time
#     """).to_data_frame()

#     time_list = df_time['time'].to_list()
#     del time_list[-1]

#     df_tu = call_graph.run("""
#         MATCH (:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
#         RETURN DISTINCT t.transformation_unit as transformation_unit
#         """).to_data_frame()

#     for ele in time_list:
#         tch = call_graph.run("""
#         MATCH (m:Molecule)-[t:PREDICTED_TRANSFORMATION]->(:Molecule)
#         WHERE m.point_in_time = """ + str(ele) + """
#         RETURN t.transformation_unit as transformation_unit, 
#                 count(t.transformation_unit) as Count_prt_""" + str(ele) + """,
#                 avg(t.normalized_combined_weight) as avg_combined_""" + str(ele) + """,
#                 avg(t.normalized_connected_weight) as avg_connect_""" + str(ele) + """
#         ORDER BY Count_prt_""" + str(ele) + """ DESC
#         """).to_data_frame()
        
#         df_tu = pd.merge(df_tu, tch, on=["transformation_unit"])
        
#     # drop columns 
#     # for combined
#     droplist_combined = [i for i in df_tu.columns if i.startswith('Count') or i.startswith('avg_connect')]
#     df_tu_combined = df_tu.drop(columns=droplist_combined, axis=1)
#     # for connected
#     droplist_connected = [i for i in df_tu.columns if i.startswith('Count') or i.startswith('avg_combined')]
#     df_tu_connected = df_tu.drop(columns=droplist_connected, axis=1)

#     # make dataframe vertical
#     # for combined
#     df_tu_combined = df_tu_combined.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='average_weight').drop('level_1',1)
#     # for connected
#     df_tu_connected = df_tu_connected.replace('', np.nan).set_index('transformation_unit').stack().reset_index(name='average_weight').drop('level_1',1)

#     # add time to dataframe
#     # for combined
#     times_repeat = len(df_tu_combined)/len(time_list)
#     times_list_combined = time_list * int(times_repeat)
#     df_tu_combined['point_in_time'] = times_list_combined
#     # for connected
#     times_repeat = len(df_tu_connected)/len(time_list)
#     times_list_connected = time_list * int(times_repeat)
#     df_tu_connected['point_in_time'] = times_list_connected

#     # create plots
#     # for combined
#     fig = px.line(df_tu_combined, x='point_in_time', y='average_weight', color='transformation_unit', symbol="transformation_unit",
#                     labels={
#                         "average_weight": "average combined weight",
#                         "point_in_time": "measurement"
#                     },
#                     title="Transformations and their weight per measurement <br>-combined weight-")
#     fig.update_layout(
#         xaxis = dict(
#             tickmode = 'linear',
#             tick0 = 0,
#             dtick = 1
#         )
#     )
#     #fig.show()

#     if export_png == 1:
#         fig.write_image(export_path + "graph_average_weight_transformations_line_combined.png")

#     if export_html == 1:
#         fig.write_html(export_path + "graph_average_weight_transformations_line_combined.html")

#     # for connected
#     fig = px.line(df_tu_connected, x='point_in_time', y='average_weight', color='transformation_unit', symbol="transformation_unit",
#                     labels={
#                         "average_weight": "average connected weight",
#                         "point_in_time": "measurement"
#                     },
#                     title="Transformations and their weight per measurement <br>-connected weight-")
#     fig.update_layout(
#         xaxis = dict(
#             tickmode = 'linear',
#             tick0 = 0,
#             dtick = 1
#         )
#     )
#     #fig.show()

#     if export_png == 1:
#         fig.write_image(export_path + "graph_average_weight_transformations_line_connected.png")
    
#     if export_html == 1:
#         fig.write_html(export_path + "graph_average_weight_transformations_line_connected.html")
    
#     print('done: create image "average weight transformations line combined and connected"')

# average_weight_transformations_bar(call_graph, export_png, export_path)
# average_weight_transformations_line(call_graph, export_png, export_html, export_path)