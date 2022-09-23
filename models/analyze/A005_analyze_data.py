# Name: Philipp Plamper 
# Date: 23. september 2022

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from A000_path_variables_analyze import path_prefix, path_prefix_csv


##################################################################################
#analyze functions################################################################
##################################################################################

# molecules per measurement
def molecules_per_snapshot_data(molecule_data, export_png, export_path):
    data = molecule_data.drop_duplicates(subset=['peak_id'])
    aggregation_functions = {'peak_charge': 'sum'}
    df_dup = data.groupby(data['measurement_id']).aggregate(aggregation_functions)

    aggregation_functions = {'peak_charge': 'sum'}
    df_count = molecule_data.groupby(molecule_data['measurement_id']).aggregate(aggregation_functions)
    help_list = np.arange(0, len(df_count), 1)
    df_count['timepoint']= help_list

    df_count['wdup'] = df_count.peak_charge - df_dup.peak_charge
    df_count['avg_mol'] = df_count.peak_charge.mean()

    mol_sd = np.std(np.array(df_count.peak_charge, df_count.timepoint))

    plt.figure(figsize=(6, 3))
    plt.suptitle('Molecules per measurement')
    plt.bar(df_count.timepoint, df_count.peak_charge, color='green')
    plt.bar(df_count.timepoint, df_count.wdup, color='orange')
    plt.plot(df_count.timepoint, df_count.avg_mol, color='purple')
    plt.plot(df_count.timepoint, df_count.avg_mol+mol_sd, linestyle='--', color='purple')
    plt.legend(['assigned average', 'standard deviation', 'assigned total', 'assigned multiple'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.plot(df_count.timepoint, df_count.avg_mol-mol_sd, linestyle='--', color='purple')
    plt.axhspan(df_count.peak_charge.mean()-mol_sd, df_count.peak_charge.mean()+mol_sd, alpha=0.15, color='purple')
    plt.xlabel('Measurement')
    plt.ylabel('Number of assigned molecules')
    plt.xticks(np.arange(0, len(df_count), 1))

    if export_png == 1:
        name = 'molecules_data'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "molecules per measurement"')
    # plt.show()

# sum of relative intensity
def sum_relative_intensity(molecule_data, export_png, export_path):
    af = {'peak_relint_tic': 'sum'}
    df_gesamt = molecule_data.groupby(molecule_data['measurement_id']).aggregate(af)
    df_gesamt['occ'] = np.arange(0, len(df_gesamt), 1)
    df_gesamt['soll'] = [1]*len(df_gesamt)
    df_gesamt['diff'] = df_gesamt['peak_relint_tic']-df_gesamt['soll']

    plt.suptitle('Sum of relative intensities per measurement')
    plt.bar(df_gesamt.occ, df_gesamt.soll, color='orange')
    plt.bar(df_gesamt.occ, df_gesamt.peak_relint_tic, color='green')
    plt.xlabel('Measurement')
    plt.ylabel('Sum of relative intensities')
    plt.legend(['Intensity of 1.0', 'Sum of relative intensities'], loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(np.arange(0, len(df_gesamt), 1))


    if export_png == 1:
        name = 'data_sum_relative_intensity'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "sum relative intensity"')
    # plt.show()

# occurrence of formula class
def occurrence_formula_class(molecule_data, export_png, export_path):
    test = {'formula_class': ['first','count']}
    df_class = molecule_data.groupby(molecule_data['formula_class'], as_index=False).aggregate(test)
    df_class_new = df_class
    df_class_new['form_class'] = df_class.formula_class['first']
    df_class_new['occ'] = df_class.formula_class['count']/df_class.formula_class['count'].sum()*100

    plt.figure(figsize=(6, 3))
    plt.suptitle('Share of formula classes')
    plt.bar(df_class_new.form_class, df_class_new.occ, color='green')
    plt.xlabel('Formula class')
    plt.ylabel('Share of formula class (%)')

    if export_png == 1:
        name = 'data_occurrence_formula_class'
        plt.savefig(export_path + name + '.png', bbox_inches='tight')

    plt.clf()
    print('done: create image "occurrence formula class"')
    # plt.show()

##################################################################################
#call functions###################################################################
##################################################################################

# load data
molecule_data = pd.read_csv(path_prefix_csv + 'ufz_all_formulas_cleaned.csv', sep=',')

# set export
export_png = 1
export_path = path_prefix

#call functions
molecules_per_snapshot_data(molecule_data, export_png, export_path)
sum_relative_intensity(molecule_data, export_png, export_path)
occurrence_formula_class(molecule_data, export_png, export_path)
