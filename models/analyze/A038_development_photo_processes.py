# Name: Philipp Plamper 
# Date: 06. march 2023

###
# SI Figure 10
# in Paper: "A temporal graph to predict chemical transformations in complex dissolved organic matter"
# Authors: Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß
###

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

def calculate_development_photo_processes(df_transformation_unit_count):
    # create empty dataframe
    df_share_processes = pd.DataFrame()

    # get share of photo addition processes
    df_photo_addition = df_transformation_unit_count[df_transformation_unit_count.is_addition == 1]
    df_share_processes['share_photo_addition'] = df_photo_addition.iloc[0:,2:].sum(axis=0).values.tolist()

    # get share of photo elimination processes
    df_photo_elimination = df_transformation_unit_count[df_transformation_unit_count.is_addition == 0]
    df_share_processes['share_photo_elimination'] = df_photo_elimination.iloc[0:,2:].sum(axis=0).values.tolist()

    return df_share_processes

def visualize_share_photo_processes(df_share_processes, df_time, photolysis):
    time_list = df_time.property_time.to_list()
    del time_list[0]

    # only if photolysis experiment
    if photolysis == 1:
        radiation_diff = df_time.rad_diff.to_list()
        del radiation_diff[0]

    fig, ax1 = plt.subplots(figsize=(12,5))
    plt.plot(time_list, df_share_processes.share_photo_addition, label='photo addition', marker='o')
    plt.plot(time_list, df_share_processes.share_photo_elimination, label='photo elimination', marker='o')
    plt.xlabel('transition', fontsize=14, fontweight='bold')
    plt.ylabel('share in %', fontsize=14, fontweight='bold')
    plt.legend(loc='upper left', fontsize=14)
    plt.xticks(np.arange(min(time_list) , max(time_list)+1, 1.0))
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    # only if photolysis experiment
    if photolysis == 1:
        # second x-axis
        ax1Ticks = ax1.get_xticks()   
        ax2Ticks = ax1Ticks
        ax2 = ax1.twiny()
        ax2.set_xticks(ax2Ticks)
        ax2.set_xbound(ax1.get_xbound())
        ax2.set_xticklabels(radiation_diff, fontsize=14)
        ax2.set_xlabel('radiation dose (kW/m$^{2}$) - difference from the last transition', fontsize=14, fontweight='bold')

    plt.tight_layout()

    name = 'graph_share_photo_processes.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    print('----------------------')
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)
    
    df_transformation_unit_count = pva.pf.get_share_transformation_units(session, pva.query_params, transition_property='share')
    df_share_processes = calculate_development_photo_processes(df_transformation_unit_count)
    df_time = pva.pf.graph_get_time(session, pva.query_params)
    visualize_share_photo_processes(df_share_processes, df_time, pva.photolysis)
    
    # end session
    session.close()