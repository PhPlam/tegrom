# Name: Philipp Plamper 
# Date: 12. october 2021

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from A000_path_variables_analyze import path_prefix, path_prefix_csv


##################################################################################
#analyze functions################################################################
##################################################################################

# molecules per measurement
def molecules_per_measurement(molecule_data, export_path):
    data = molecule_data.drop_duplicates(subset=['peak_id'])
    aggregation_functions = {'peak_charge': 'sum'}
    df_dup = data.groupby(data['measurement_id']).aggregate(aggregation_functions)

    aggregation_functions = {'peak_charge': 'sum'}
    df_count = molecule_data.groupby(molecule_data['measurement_id']).aggregate(aggregation_functions)
    help_list = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    df_count['timepoint']= help_list

    df_count['wdup'] = df_count.peak_charge - df_dup.peak_charge
    df_count['avg_mol'] = df_count.peak_charge.mean()

    mol_sd = np.std(np.array(df_count.peak_charge, df_count.timepoint))

    plt.figure(figsize=(6, 3))
    plt.suptitle('Zugewiesene Moleküle je Messung')
    plt.bar(df_count.timepoint, df_count.peak_charge, color='green')
    plt.bar(df_count.timepoint, df_count.wdup, color='orange')

    plt.plot(df_count.timepoint, df_count.avg_mol, color='purple')
    plt.plot(df_count.timepoint, df_count.avg_mol+mol_sd, linestyle='--', color='purple')

    plt.legend(['durchschnittlich zugewiesen', 'Standardabweichung', 'insgesamt zugewiesen', 'Mehrfachzuweisungen'], loc='upper left', bbox_to_anchor=(1, 1))

    plt.plot(df_count.timepoint, df_count.avg_mol-mol_sd, linestyle='--', color='purple')
    plt.axhspan(df_count.peak_charge.mean()-mol_sd, df_count.peak_charge.mean()+mol_sd, alpha=0.15, color='purple')

    plt.xlabel('Messpunkt')
    plt.ylabel('Anzahl an zugewiesenen Molekülen')
    x = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    plt.xticks(x)

    name = 'data_molecules_per_measurement'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    print('done: create image "molecules per measurement"')
    # plt.show()

# sum of relative intensity
def sum_relative_intensity(molecule_data, export_path):
    af = {'peak_relint_tic': 'sum'}
    df_gesamt = molecule_data.groupby(molecule_data['measurement_id']).aggregate(af)
    df_gesamt['occ'] = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    df_gesamt['soll'] = [1,1,1,1,1,1,1,1,1,1,1,1,1]
    df_gesamt['diff'] = df_gesamt['peak_relint_tic']-df_gesamt['soll']

    plt.suptitle('Summe der relativen Intensitäten über alle Messpunkte')
    plt.bar(df_gesamt.occ, df_gesamt.peak_relint_tic, color='green')
    plt.bar(df_gesamt.occ, df_gesamt.soll, color='orange')
    plt.xlabel('Messpunkt')
    plt.ylabel('Summe der relativen Intensitäten')
    plt.legend(['summierte normalisierte Intensität', 'normalisierte Intensität von 1.0'], loc='upper left', bbox_to_anchor=(1, 1))
    x = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    plt.xticks(x)

    name = 'data_sum_relative_intensity'
    plt.savefig(export_path + name + '.png', bbox_inches='tight')
    print('done: create image "sum relative intensity"')
    # plt.show()

##################################################################################
#call functions###################################################################
##################################################################################

# load data
molecule_data = pd.read_csv(path_prefix_csv + 'ufz_all_formulas_raw.csv', sep=';')

# set export path
export_path = path_prefix

#call functions
molecules_per_measurement(molecule_data, export_path)
sum_relative_intensity(molecule_data, export_path)
