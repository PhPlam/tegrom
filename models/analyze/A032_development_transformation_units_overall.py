# Name: Philipp Plamper 
# Date: 26. january 2023

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy import stats

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

def calculate_increase(df_transformation_unit_count, df_time):
    time_list = df_time['property_time'].to_list()
    del time_list[-1]

    transformation_unit_dict_list = []
    for tu in df_transformation_unit_count.transformation_unit:
        pick_tu = df_transformation_unit_count[df_transformation_unit_count.transformation_unit == tu]
        values = pick_tu.iloc[0,2:].values.tolist()

        # calculate angle 
        res = stats.linregress(time_list, values)
        angle = np.rad2deg(np.arctan((res.slope*len(time_list))/(len(time_list))))
        
        # calculate increase
        increase = np.tan(angle*(np.pi/180))*100    
        
        tu_dict = {
            'tu': tu,
            'is_addition': pick_tu.is_addition.values[0],
            'increase': increase,
            'share_mean_perc': np.mean(values)
        }
        transformation_unit_dict_list.append(tu_dict)
        

    df_transformation_unit = pd.DataFrame(transformation_unit_dict_list)
    df_transformation_unit = df_transformation_unit.sort_values(by=['increase'], ascending=False).reset_index(drop=True)

    print('done: calculate increase')
    return df_transformation_unit

def visualize_transformation_units(df_tu, query_params):
    fig = plt.figure(figsize=(12,6))
    col = np.where(df_tu.is_addition==1,'green','orange')

    # first plot
    ax1 = plt.subplot(211)
    plt.bar(df_tu.tu, df_tu.share_mean_perc, width=0.6, color=col)
    plt.xlabel('transformation unit', fontsize=15, fontweight='bold')
    plt.ylabel('average \n share in %', fontsize=15, fontweight='bold')
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(np.arange(0, max(df_tu.share_mean_perc), 1), fontsize=14)
    plt.axhline(y=df_tu.share_mean_perc.mean(), color='r', linestyle='-', label='average overall')

    orange_patch = mpatches.Patch(color='orange', label='photo elimination')
    green_patch = mpatches.Patch(color='green', label='photo addition')
    red_line = Line2D([0], [0], label='average overall', color='red')
    plt.legend(handles=[orange_patch, green_patch, red_line], loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)

    # second plot
    plt.subplot(212, sharex=ax1)
    plt.bar(df_tu.tu, df_tu.increase, width=0.6, color=col)
    plt.ylabel('increase \n share in %', fontsize=15, fontweight='bold')
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(np.arange(np.round(min(df_tu.increase), 0), max(df_tu.increase), 10), fontsize=14)
    #plt.xticks(color='black')
    plt.xlabel('transformation unit', fontsize=15, fontweight='bold')
    plt.axhline(y=0, color='r', linestyle='-', label='no increase')
    orange_patch = mpatches.Patch(color='orange', label='photo elimination')
    green_patch = mpatches.Patch(color='green', label='photo addition')
    red_line = Line2D([0], [0], label='no increase', color='red')
    plt.legend(handles=[orange_patch, green_patch, red_line], loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)

    plt.tight_layout()
    
    name = 'graph_share_transformation_units.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)

    df_transformation_unit_count = pva.pf.get_share_transformation_units(session, pva.query_params)
    df_time = pva.pf.graph_get_time(session, pva.query_params)
    df_transformation_unit_properties = calculate_increase(df_transformation_unit_count, df_time)
    visualize_transformation_units(df_transformation_unit_properties, pva.query_params)

    # end session
    session.close()