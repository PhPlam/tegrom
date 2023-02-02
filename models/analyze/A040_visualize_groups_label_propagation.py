# Name: Philipp Plamper 
# Date: 02. february 2023

import numpy as np
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

# get member of top five communities
def member_top_five(session, query_params, community_list, algorithm):
    df_communities = session.run(
        "MATCH (m:" + query_params['label_node'] + ") "
        "WHERE m.community_" + algorithm + " IN " + str(community_list) + " "
        "RETURN m." + query_params['prop_node_name'] + " as molecular_formula, "
        "m.community_" + algorithm + " as community, "
        "m." + query_params['prop_extra_4'] + query_params['prop_extra_1'] + " as oc, "
        "m." + query_params['prop_extra_2'] + query_params['prop_extra_1'] + " as hc, "
        "m." + query_params['prop_extra_16'] + " as formula_mass"
    ).to_df()
    
    print('done: get member of top five communities')
    return df_communities

# visualize the communities
def visualize_communities(df_communities, algorithm):
    ps = 15
    fig = plt.figure(figsize=(14,8))

    plt.subplot(2,2,1)
    plt.scatter(df_communities[df_communities.community == community_list[0]].oc, df_communities[df_communities.community == community_list[0]].hc, c='black', s=ps, label='group 1')
    plt.scatter(df_communities[df_communities.community == community_list[1]].oc, df_communities[df_communities.community == community_list[1]].hc, c='r', s=ps, label='group 2')
    plt.scatter(df_communities[df_communities.community == community_list[2]].oc, df_communities[df_communities.community == community_list[2]].hc, c='green', s=ps, label='group 3')
    plt.scatter(df_communities[df_communities.community == community_list[3]].oc, df_communities[df_communities.community == community_list[3]].hc, c='blue', s=ps, label='group 4')
    plt.scatter(df_communities[df_communities.community == community_list[4]].oc, df_communities[df_communities.community == community_list[4]].hc, c='purple', s=ps, label='group 5')
    plt.xlabel('O/C', fontsize=16, fontweight= 'bold')
    plt.ylabel('H/C', fontsize=16, fontweight= 'bold')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    plt.subplot(2,2,2)
    plt.scatter(df_communities[df_communities.community == community_list[0]].formula_mass, df_communities[df_communities.community == community_list[0]].hc, c='black', s=ps, label='group 1')
    plt.scatter(df_communities[df_communities.community == community_list[1]].formula_mass, df_communities[df_communities.community == community_list[1]].hc, c='r', s=ps, label='group 2')
    plt.scatter(df_communities[df_communities.community == community_list[2]].formula_mass, df_communities[df_communities.community == community_list[2]].hc, c='green', s=ps, label='group 3')
    plt.scatter(df_communities[df_communities.community == community_list[3]].formula_mass, df_communities[df_communities.community == community_list[3]].hc, c='blue', s=ps, label='group 4')
    plt.scatter(df_communities[df_communities.community == community_list[4]].formula_mass, df_communities[df_communities.community == community_list[4]].hc, c='purple', s=ps, label='group 5')
    plt.xlabel('Formula Mass', fontsize=16, fontweight= 'bold')
    plt.ylabel('H/C', fontsize=16, fontweight= 'bold')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14, loc='upper left', bbox_to_anchor=(1, 1), markerscale=2.5)

    plt.figtext(0, 1, '(A)', fontsize=16, fontweight='bold')
    plt.figtext(0.445, 1, '(B)', fontsize=16, fontweight='bold')

    plt.tight_layout()

    name = 'graph_visualize_communities_' + algorithm + '.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    print('----------------------')
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_light)
    
    community_list = [x for x in pva.pf.get_properties_top_communities(session, pva.query_params, algorithm='lpa').community]
    df_communities = member_top_five(session, pva.query_params, community_list, algorithm='lpa')
    visualize_communities(df_communities, algorithm='lpa')
    
    # end session
    session.close()