# Name: Philipp Plamper
# Date: 09. march 2023

import pandas as pd
from progress.bar import Bar
import P000_path_variables_preprocess as pvp

##################################################################################
#calculate possible transformations###############################################
##################################################################################

# calculate new molecules from given molecules and transformation units
def calculate_formula_relationships(formula_strings, transformation_unit):
    # create empty list to store dictionaries with calculated relationships
    formula_list = []
    # initiate progress bar
    bar_calculate_relationships = Bar('calculate relationships:', max = len(formula_strings.index))

    # iterate through dataframe of molecular formulas
    for row1 in formula_strings.itertuples():
        bar_calculate_relationships.next()
        # iterate through dataframe of transformation units
        for row2 in transformation_unit.itertuples():
            # calculate new molecules from given molecules and transformation units in direction: photoaddition
            # check if transformation unit exist as photo addition in data
            if int(row2.plus) == 1:
                # define exist as True
                # if molecule of calculated relationship has atom < 0 
                # jumps to False and code skips the relationship
                exist = True
                # create empty dictionary for new formulas
                formula_dict = {}
                # initiate atoms per formula with 0
                new_C = new_H = new_O = new_N = new_S = 0

                # calculate possible new molecule
                # calculation: formula - transformation_unit = new_formula
                # skip if count < 0
                new_C = row1.C - row2.C if row1.C - row2.C >= 0 else -1
                if new_C == -1: exist = False
                new_H = row1.H - row2.H if row1.H - row2.H >= 0 else -1
                if new_H == -1: exist = False
                new_O = row1.O - row2.O if row1.O - row2.O >= 0 else -1
                if new_O == -1: exist = False
                new_N = row1.N - row2.N if row1.N - row2.N >= 0 else -1
                if new_N == -1: exist = False
                new_S = row1.S - row2.S if row1.S - row2.S >= 0 else -1
                if new_S == -1: exist = False

                # create dictionary with results
                # only if calculated molecule can exist
                if exist == True:
                    formula_dict = {
                        'formula_string': row1.formula_string,
                        'transformation_unit': row2.element,
                        'is_addition' : 1,
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

            # calculate new molecules from given molecules and transformation units in direction: photodegradation
            # choose if transformation unit exist as photo elimination in data
            if int(row2.minus) == 1:
                # create empty dictionary for new formulas
                formula_dict = {}
                # initiate atoms per formula with 0
                new_C = new_H = new_O = new_N = new_S = 0

                # calculate possible new atom count in molecule
                # calculation: formula + transformation_unit = new_formula
                new_C = row1.C + row2.C
                new_H = row1.H + row2.H
                new_O = row1.O + row2.O
                new_N = row1.N + row2.N
                new_S = row1.S + row2.S

                # create dictionary with results
                formula_dict = {
                    'formula_string': row1.formula_string,
                    'transformation_unit': row2.element,
                    'is_addition': 0,
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

    bar_calculate_relationships.finish()
    print('done: calculate new molecules photoaddition')
    return formula_list

# create strings from calculated molecules
def create_strings_from_molecules(merged_molecule_list):
    molecule_df = pd.DataFrame(merged_molecule_list)
    help_list = []
    # initiate progress bar
    bar_build_strings = Bar('build strings from molecules:', max = len(molecule_df.index))

    # take calculated atoms and append to string -> structure: 'CHNOS'
    for row in molecule_df.itertuples():
        bar_build_strings.next()
        new_molecule = ''
        if row.new_C > 0: new_molecule = 'C' + str(row.new_C)
        if row.new_H > 0: new_molecule = new_molecule + ' H' + str(row.new_H)
        if row.new_N > 0: new_molecule = new_molecule + ' N' + str(row.new_N)
        if row.new_O > 0: new_molecule = new_molecule + ' O' + str(row.new_O)
        if row.new_S > 0: new_molecule = new_molecule + ' S' + str(row.new_S)

        # append new formula string to list
        help_list.append(new_molecule)
    
    # append new formula strings to dataframe
    molecule_df['new_formula'] = help_list
    bar_build_strings.finish()
    print('done: create strings from molecules')
    return molecule_df

# check existence of strings in the molecule data
def check_existence_of_strings(df_added_strings):
    occurence_list = []
    # initiate progress bar
    bar_check_existence = Bar('check existence:', max = len(df_added_strings.index))

    # check if molecule exist in molecule data
    for row in df_added_strings.itertuples():
        bar_check_existence.next()
        if row.new_formula in formula_strings['formula_string'].values:
            occurence_list.append(1)
        else:
            occurence_list.append(0)

    bar_check_existence.finish()

    df_added_strings['occur'] = occurence_list
    # drop rows with molecules that does not exist
    df_added_strings.drop(df_added_strings[df_added_strings.occur == 0].index, inplace=True)
    molecule_df = df_added_strings.drop(columns=['occur'])
    print('done: check existence of molecules')
    return molecule_df

# create strings from atoms of transformation units
def create_strings_transformation_unit(df_molecules):
    tu_list = []
    # initiate progress bar
    bar_create_strings_transformation_units = Bar('create strings of transformation units:', max = len(df_molecules.index))

    for row in df_molecules.itertuples(): # index=False
        bar_create_strings_transformation_units.next()
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

    bar_create_strings_transformation_units.finish()    
    df_molecules['transformation_unit'] = tu_list
    print('done: create strings for transformation unit')
    return df_molecules

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':

    # define data
    formula_strings = pvp.load_csv(pvp.unique_molecules, seperator=[',', ';'])
    transformation_unit = pvp.load_csv(pvp.file_transformation_units, seperator=[',', ';'])

    # calculate
    calculated_relationships = calculate_formula_relationships(formula_strings, transformation_unit)
    df_added_strings = create_strings_from_molecules(calculated_relationships)
    df_molecules = check_existence_of_strings(df_added_strings)
    calculated_transformations = create_strings_transformation_unit(df_molecules)

    #export
    pvp.export_csv(pvp.relationships, calculated_transformations)