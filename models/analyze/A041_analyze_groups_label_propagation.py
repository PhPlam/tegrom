# Name: Philipp Plamper 
# Date: 24. march 2023

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

# create dataframe with community properties and export
def export_properties(session, properties_communities, query_params, algorithm):
    top_list = [x for x in properties_communities.community]

    property_list_community = []
    i = 0
    for community in top_list:
        
        df_tu_top_five_occurrence = session.run(
            "MATCH (m:" + query_params['label_node'] + query_params['nodes_light'] + ")-[ct:" + query_params['label_chemical_edge'] + "]->(m2:" + query_params['label_node'] + query_params['nodes_light'] + ") "
            "WHERE m.community_" + algorithm + " = " + str(community) + " "
                "AND m2.community_" + algorithm + " = " + str(community) + " "
            "WITH ct." + query_params['prop_edge_value_1'] + " as tu, "
                "sum(ct." + query_params['prop_extra_9'] + ") as tu_cnt "
            "RETURN tu, tu_cnt "
            "ORDER BY tu_cnt DESC "
            "LIMIT 5"
        ).to_df()       
        
        # dictionary of properties
        dict_group = {
            "community": properties_communities.community[i],
            "member": properties_communities.member[i],
            "avg_hc": properties_communities.avg_hc[i],
            "avg_oc": properties_communities.avg_oc[i],
            "sum_ct": properties_communities.sum_ct[i],
            "sum_prt": properties_communities.sum_prt[i],
            "avg_ct": properties_communities.avg_ct[i],
            "avg_prt": properties_communities.avg_prt[i],
            "avg_occurrence": properties_communities.cnt_occ[i],
            "avg_intensity": properties_communities.avg_int[i],
            'top_tu': df_tu_top_five_occurrence.tu.to_list()
        }

        # list of dictionaries
        property_list_community.append(dict_group)
        i+=1
        
    df_groups = pd.DataFrame(property_list_community)

    name = 'table_analyze_communities_' + algorithm + '.csv'
    df_groups.to_csv(pva.export_path_prefix + name, index=False)
    print('done: create table ' + name)

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    print('----------------------')
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)
    
    properties_communities = pva.pf.get_properties_top_communities(session, pva.query_params, algorithm='lpa')
    export_properties(session, properties_communities, pva.query_params, algorithm='lpa')

    # end session
    session.close()