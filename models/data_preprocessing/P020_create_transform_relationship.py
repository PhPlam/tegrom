# Name: Philipp Plamper
# Date: 11. may 2021

import pandas as pd
from progress.bar import Bar
from P000_path_variables_preprocess import formula_strings, transformation_unit, export_path_create


#variables
formula_strings = formula_strings
transformation_unit = transformation_unit

##################################################################################
#create csv with transformations##################################################
##################################################################################

# calculate both directions of transformations
# enables possibility to define important transformation_units in both ways

def new_calculate_transformations():

    # calculation: formula - transformation_unit = new_formula
    formula_list = []
    bar_one = Bar('calculate new formulas:', max = len(formula_strings.index))


    # calculate new formulas #########################################################
    # file with unique formula strings
    for row1 in formula_strings.itertuples():
        bar_one.next()
        # file with all transformation_units
        for row2 in transformation_unit.itertuples():
            # choose if transformation is useful in this model
            if row2.plus == 0:
                continue

            # create empty dictionary for new formulas
            formula_dict = {}
            # initiate atoms per formula with 0
            new_C = new_H = new_O = new_N = new_S = 0

            # calculate possible new atom count in molecule
            # skip if count < 0
            new_C = row1.C - row2.C if row1.C - row2.C >= 0 else -1
            if new_C == -1: continue
            new_H = row1.H - row2.H if row1.H - row2.H >= 0 else -1
            if new_H == -1: continue
            new_O = row1.O - row2.O if row1.O - row2.O >= 0 else -1
            if new_O == -1: continue
            new_N = row1.N - row2.N if row1.N - row2.N >= 0 else -1
            if new_N == -1: continue
            new_S = row1.S - row2.S if row1.S - row2.S >= 0 else -1
            if new_S == -1: continue

            # create dictionary with results
            formula_dict = {
                'formula_string': row1.formula_string,
                'transformation_unit': row2.element,
                'new_C': new_C,
                'new_H': new_H,
                'new_O': new_O,
                'new_N': new_N,
                'new_S': new_S,
                'tu_C': row2.C,
                'tu_H': row2.H,
                'tu_O': row2.O,
                'tu_N': row2.N,
                'tu_S': row2.S
            }
            # append dictionary to list
            formula_list.append(formula_dict)

    bar_one.finish()

    
    # test ##############################################################################
    bar_onehalf = Bar('calculate new formulas:', max = len(formula_strings.index))

    for row1 in formula_strings.itertuples():
        bar_onehalf.next()
        # file with all transformation_units
        for row2 in transformation_unit.itertuples():
            # choose if transformation is useful in this model
            if row2.minus == 0:
                continue

            # create empty dictionary for new formulas
            formula_dict = {}
            # initiate atoms per formula with 0
            new_C = new_H = new_O = new_N = new_S = 0

            # calculate possible new atom count in molecule
            new_C = row1.C + row2.C
            new_H = row1.H + row2.H
            new_O = row1.O + row2.O
            new_N = row1.N + row2.N
            new_S = row1.S + row2.S

            # create dictionary with results
            formula_dict = {
                'formula_string': row1.formula_string,
                'transformation_unit': row2.element,
                'new_C': new_C,
                'new_H': new_H,
                'new_O': new_O,
                'new_N': new_N,
                'new_S': new_S,
                'tu_C': (-1)*row2.C if row2.C != 0 else 0,
                'tu_H': (-1)*row2.H if row2.H != 0 else 0,
                'tu_O': (-1)*row2.O if row2.O != 0 else 0,
                'tu_N': (-1)*row2.N if row2.N != 0 else 0,
                'tu_S': (-1)*row2.S if row2.S != 0 else 0
            }
            # append dictionary to list
            formula_list.append(formula_dict)

    bar_onehalf.finish()
    # test ende ##########################################################################
    

    # create new dataframe from new list of dictionaries
    molecule_df = pd.DataFrame(formula_list)
    help_list = []

    bar_two = Bar('build new strings:', max = len(molecule_df.index))

    # build new strings ##############################################################
    # build new molecule from dataframe columns
    # take calculated atoms and append to string -> structure: 'CHNOS'
    for row in molecule_df.itertuples():
        bar_two.next()
        new_molecule = ''
        if row.new_C > 0: new_molecule = 'C' + str(row.new_C)
        if row.new_H > 0: new_molecule = new_molecule + ' H' + str(row.new_H)
        if row.new_N > 0: new_molecule = new_molecule + ' N' + str(row.new_N)
        if row.new_O > 0: new_molecule = new_molecule + ' O' + str(row.new_O)
        if row.new_S > 0: new_molecule = new_molecule + ' S' + str(row.new_S)

        # append new formula string to list
        help_list.append(new_molecule)

    bar_two.finish()

    # append new formula strings to dataframe
    molecule_df['new_formula'] = help_list

    occurence_list = []
    bar_three = Bar('check existence:', max = len(molecule_df.index))

    # check existence ################################################################
    # check if molecule transformations exist in molecule table
    for row in molecule_df.itertuples():
        bar_three.next()
        if row.new_formula in formula_strings['formula_string'].values:
            occurence_list.append(1)
        else:
            occurence_list.append(0)

    bar_three.finish()

    molecule_df['occur'] = occurence_list
    molecule_df.drop(molecule_df[molecule_df.occur == 0].index, inplace=True)
    molecule_df = molecule_df.drop(columns=['occur'])


    # set transformation_unit strings ###################################################
    tu_list = []

    #for index, row in data.iterrows():
    for row in molecule_df.itertuples(): # index=False
        tu_string = ""

        if row.tu_C < 0: tu_string = "-" + tu_string + "C" + str(abs(row.tu_C)) + " "
        elif row.tu_C > 0: tu_string = tu_string + "C" + str(row.tu_C) + " "
        else: tu_string

        if row.tu_H < 0: tu_string = tu_string + "-H" + str(abs(row.tu_H)) + " "
        elif row.tu_H > 0: tu_string = tu_string + "H" + str(row.tu_H) + " "
        else: tu_string

        if row.tu_O < 0: tu_string = tu_string + "-O" + str(abs(row.tu_O)) + " "
        elif row.tu_O > 0: tu_string = tu_string + "O" + str(row.tu_O) + " "
        else: tu_string

        if row.tu_N < 0: tu_string = tu_string + "-N" + str(abs(row.tu_N)) + " "
        elif row.tu_N > 0: tu_string = tu_string + "N" + str(row.tu_N) + " "
        else: tu_string

        if row.tu_S < 0: tu_string = tu_string + "-S" + str(abs(row.tu_S)) + " "
        elif row.tu_S > 0: tu_string = tu_string + "S" + str(row.tu_S) + " "
        else: tu_string

        # print(tu_string)
        tu_string = tu_string.rstrip()
        tu_list.append(tu_string)
    
    molecule_df['transformation_unit'] = tu_list
    
    ##################################################################################
    #export csv#######################################################################
    ##################################################################################

    export_path = export_path_create
    molecule_df.to_csv(export_path, sep=',', encoding='utf-8', index=False, float_format='%.f')


    ##################################################################################
    ##################################################################################
    ##################################################################################

new_calculate_transformations()