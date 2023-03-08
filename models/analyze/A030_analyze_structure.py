# Name: Philipp Plamper 
# Date: 06. march 2023

###
# Figure 4
# in Paper: "A temporal graph to predict chemical transformations in complex dissolved organic matter"
# Authors: Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß
###

import numpy as np
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

def analyze_structure(session, query_params, df_time, photolysis):
    
    ### get the data ################################

    ### get time ###
    standard_deviation = np.std(np.array(df_time['count_nodes'], df_time['property_time']))

    # only if photolysis experiment
    if photolysis == 1: 
        radiation_diff = df_time.rad_diff.to_list()
        del radiation_diff[0]

    ### get trends ###
    # increasing 
    trend = 'increasing'
    lower = pva.upper_limit
    upper = 100 # choose higher number than possible in data, important for generic cypher query structure
    trend_incr = pva.pf.graph_get_member_intensity_trend(session, query_params, lower, upper, trend)
    
    # decreasing
    trend = 'decreasing'
    lower = 0 # choose lower number than possible in data, important for generic cypher query structure
    upper = pva.lower_limit
    trend_decr = pva.pf.graph_get_member_intensity_trend(session, query_params, lower, upper, trend)

    # consistent
    trend = 'consistent'
    lower = pva.lower_limit + 1e-10
    upper = pva.upper_limit - 1e-10
    trend_cons = pva.pf.graph_get_member_intensity_trend(session, query_params, lower, upper, trend)

    ### get transformations ###
    # POTENTIAL_TRANSFORMATIONS
    edge_type = query_params['label_potential_edge']
    transformations_type_a = pva.pf.graph_get_transformations(session, edge_type, query_params)

    # PREDICTED_TRANSFORMATIONS
    edge_type = query_params['label_predicted_edge']
    transformations_type_b = pva.pf.graph_get_transformations(session, edge_type, query_params)


    ### create the plot #############################

    fig = plt.figure(figsize=(14,9))

    # first plot
    plt.subplot(311)
    plt.bar(df_time.property_time, df_time.count_nodes, color='brown', width=0.6)
    plt.axhline(df_time.count_nodes.mean(), color='purple', label='average', linewidth=1)
    plt.axhline(df_time.count_nodes.mean()-standard_deviation, linestyle='--', color='purple', label='standard deviation', linewidth=0.5)
    plt.axhline(df_time.count_nodes.mean()+standard_deviation, linestyle='--', color='purple', linewidth=0.5)
    plt.axhspan(df_time.count_nodes.mean()-standard_deviation, df_time.count_nodes.mean()+standard_deviation, alpha=0.05, color='purple')
    plt.xlabel('time', fontsize=16, fontweight='bold')
    plt.ylabel('nodes \n "Molecule"', fontsize=15, fontweight='bold')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
    plt.xticks(np.arange(0, len(df_time), 1), fontsize=14)
    plt.yticks(fontsize=14)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # second plot
    ax_sec = plt.subplot(312)#, sharex=ax1)
    plt.bar(trend_incr.property_time, trend_incr.increasing + trend_decr.decreasing + trend_cons.consistent, color = 'darkmagenta', width=0.6)
    plt.bar(trend_incr.property_time, trend_incr.increasing + trend_decr.decreasing, color = 'darkorange', width=0.6)
    plt.bar(trend_incr.property_time, trend_incr.increasing, color = 'olivedrab', width=0.6)
    plt.xlabel('transition', fontsize=16, fontweight='bold')
    plt.ylabel('edges \n "SAME_AS"', fontsize=15, fontweight='bold')
    plt.legend(['consistent intensity', 'decreasing intensity', 'inreasing intensity'], loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
    plt.xticks(np.arange(1, len(df_time), 1), fontsize=14)
    plt.yticks(fontsize=14)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # only if photolysis experiment
    if photolysis == 1: 
        # second plot - second x-axis
        axTicks = ax_sec.get_xticks()   
        ax_rad = ax_sec.twiny()
        ax_rad.set_xticks(axTicks)
        ax_rad.set_xbound(ax_sec.get_xbound())
        ax_rad.set_xticklabels(radiation_diff, fontsize=14)
        ax_rad.set_xlabel('radiation dose (kW/m$^{2}$) - difference from the last transition', fontsize=14, fontweight='bold')

    # third plot
    ax = plt.subplot(313)#, sharex=ax_sec)
    ax.bar(transformations_type_a.property_time-0.2, transformations_type_a.count_relationships, color='forestgreen', width=0.4, label='"POTENTIAL_TRANSFORMATION"')
    ax.set_xlabel('transition', fontsize=16, fontweight='bold')
    ax.set_xticks(np.arange(1, len(df_time), 1), fontsize=13)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set_ylabel('number of \n transformations', fontsize=15, fontweight='bold', color='forestgreen')
    ax.yaxis.set_tick_params(labelsize=14)
    ax.xaxis.set_tick_params(labelsize=14)
    ax.legend(loc='best')

    # third plot - second y-axis
    ax2 = ax.twinx()
    ax2.bar(transformations_type_b.property_time+0.2, transformations_type_b.count_relationships, color='sandybrown', width=0.4, label='"PREDICTED_TRANSFORMATION"')
    ax2.set_ylabel('number of \n transformations', fontsize=15, fontweight='bold', color='sandybrown')
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax2.yaxis.set_tick_params(labelsize=14)
    ax2.set_yticks(np.arange(0, max(transformations_type_b.count_relationships), 1000))
    ax2.legend(loc='best', bbox_to_anchor=(0.57, 1))

    # only if photolysis experiment
    if photolysis == 1: 
        # third plot - second x-axis
        axTicks = ax.get_xticks()   
        ax_rad = ax.twiny()
        ax_rad.set_xticks(axTicks)
        ax_rad.set_xbound(ax.get_xbound())
        ax_rad.set_xticklabels(radiation_diff, fontsize=14)
        ax_rad.set_xlabel('radiation dose (kW/m$^{2}$) - difference from the last transition', fontsize=14, fontweight='bold')


    plt.figtext(-0.02, 0.96, '(A)', fontsize=16, fontweight='bold')
    plt.figtext(-0.02, 0.64, '(B)', fontsize=16, fontweight='bold')
    plt.figtext(-0.02, 0.32, '(C)', fontsize=16, fontweight='bold')

    plt.tight_layout()

    name = 'graph_structure.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    print('----------------------')
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)

    df_time = pva.pf.graph_get_time(session, pva.query_params)
    analyze_structure(session, pva.query_params, df_time, pva.photolysis)

    # end session
    session.close()