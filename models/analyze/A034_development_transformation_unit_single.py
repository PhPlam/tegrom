# Name: Philipp Plamper 
# Date: 27. january 2023

import numpy as np
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################

# choose a transformation unit to visualize the development
def get_single_transformation_unit(df_transformation_unit_count):

    # choose transformation unit from all occurring transformation units
    print('list of all transformation units: ')
    list_transformation_units = df_transformation_unit_count.transformation_unit.to_list()
    print(list_transformation_units)
    transformation_unit = input('Choose a transformation unit (default: ' + list_transformation_units[0] + '): ') or list_transformation_units[0]
    
    # get properties of picked transformation unit
    pick_transformation_unit  = df_transformation_unit_count[df_transformation_unit_count.transformation_unit == transformation_unit].copy()
    
    # get standard deviation of share
    pick_transformation_unit['std'] = np.std(pick_transformation_unit.iloc[0,2:].values.tolist())

    return pick_transformation_unit


# visualize development of a single transformation unit
def visualize_single_transformation_unit(single_transformation_unit, df_time):
    list_share = single_transformation_unit.iloc[0,2:-1].values.tolist()
    time_list = df_time.property_time.to_list()
    del time_list[0]
    radiation_diff = df_time.rad_diff.to_list()
    del radiation_diff[0]
    std_tu = single_transformation_unit.iloc[0,-1]

    fig = plt.figure(figsize=(12,4))

    # first plot
    ax1 = plt.subplot()
    plt.plot(time_list, list_share, marker='o', label='transformation_unit', c='b', linestyle='dashed', linewidth=1.5, markersize=10)
    # first - tu - avg, sd
    plt.axhline(np.mean(list_share), c='purple', linewidth=0.5, label='average')
    plt.axhline(np.mean(list_share)+std_tu, linewidth=0.5, linestyle='--', color='purple', label='standard deviation')
    plt.axhline(np.mean(list_share)-std_tu, linewidth=0.5, linestyle='--', color='purple')
    plt.axhspan(np.mean(list_share)-std_tu, np.mean(list_share)+std_tu, alpha=0.05, color='purple')
    # first - legend
    plt.legend(fontsize=14, loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel('transition', fontsize=15, fontweight='bold')
    plt.xticks(fontsize=14)
    plt.yticks(np.arange(np.round(min(list_share),0), max(list_share), 1), fontsize=14)
    plt.ylabel('share in %', fontsize=15, fontweight='bold')
    plt.xticks(np.arange(min(time_list), max(time_list)+1, 1.0))
    # first - second x
    axTicks = ax1.get_xticks()   
    ax2 = ax1.twiny()
    ax2.set_xticks(axTicks)
    ax2.set_xbound(ax1.get_xbound())
    ax2.set_xticklabels(radiation_diff, fontsize=13)
    ax2.set_xlabel('difference radiation dose (kW/m$^{2}$)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    
    name = 'graph_development_single_transformation_unit.png'
    plt.savefig(pva.export_path_prefix + name, dpi=150, bbox_inches='tight')
    print('done: create plot ' + name)


##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)

    df_transformation_unit_count = pva.pf.get_share_transformation_units(session, pva.query_params, transition_property='share')
    single_transformation_unit = get_single_transformation_unit(df_transformation_unit_count)
    df_time = pva.pf.graph_get_time(session, pva.query_params)
    visualize_single_transformation_unit(single_transformation_unit, df_time)
    
    # end session
    session.close()