# Name: Philipp Plamper 
# Date: 27. january 2023

###
# SI Figure 6
# in Paper: "A temporal graph to predict chemical transformations in complex dissolved organic matter"
# Authors: Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß
###

import numpy as np
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

def get_out_degree(session, query_params):
    df_degree = session.run(
        "MATCH (m:" + query_params['label_node'] + ")-[prt:" + query_params['label_predicted_edge'] + "]->(:" + query_params['label_node'] + ") "
        "WITH m." + query_params['prop_node_name'] + " as fs, m." + query_params['prop_node_snapshot'] + " as pit, count(prt) as cnt_prt "
        "RETURN cnt_prt, count(cnt_prt) as sum_cnt "
        "ORDER BY cnt_prt"
    ).to_df()

    print('done: calculate out degree')
    return df_degree


def visualize_out_degree(df_degree):
    fig = plt.subplots(figsize=(5,3))
    plt.bar(df_degree.cnt_prt, df_degree.sum_cnt, width=0.6)
    plt.xlabel('number of outgoing predicted transformations', fontweight='bold')
    plt.ylabel('number of nodes', fontweight='bold')
    plt.xticks(np.arange(1, len(df_degree)+1, 1))
    plt.tight_layout()

    name = 'graph_out_degree.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    print('----------------------')
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)

    df_degree = get_out_degree(session, pva.query_params)
    visualize_out_degree(df_degree)
    
    # end session
    session.close()