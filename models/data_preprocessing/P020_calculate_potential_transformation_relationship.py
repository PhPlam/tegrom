# Name: Philipp Plamper
# Date: 09. march 2023

###
# SI Algorithm 1
# in Paper: "A temporal graph to predict chemical transformations in complex dissolved organic matter"
# Authors: Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß
###

import pandas as pd
from progress.bar import Bar
import P000_path_variables_preprocess as pvp

##################################################################################
#calculate possible transformations###############################################
##################################################################################

# calculate new molecules from given molecules and transformation units
# see SI Algorithm 1
def calculate_formula_relationships(formula_strings, transformation_unit):
    # create empty list to store dictionaries with calculated relationships
    # see algorithm line 4-5
    formula_list = []
    # initiate progress bar
    bar_calculate_relationships = Bar('calculate relationships:', max = len(formula_strings.index))

    # iterate through dataframe of molecular formulas
    # see algorithm line 6-7
    for mol_formula in formula_strings.itertuples():
        bar_calculate_relationships.next()
        # iterate through dataframe of transformation units
        # see algorithm line 8-9
        for trans_unit in transformation_unit.itertuples():
            # calculate new molecules from given molecules and transformation units in direction: photoaddition
            # check if transformation unit exist as photo addition in data
            # see algorithm line 10-11
            if int(trans_unit.plus) == 1:
                # create empty dictionary for new formulas
                formula_dict = {}
                # initiate atoms per formula with 0
                new_C = new_H = new_O = new_N = new_S = 0

                # calculate possible new atom count in molecule
                # calculation: formula + transformation_unit = new_formula
                # see algorithm line 12-14
                new_C = mol_formula.C + trans_unit.C
                new_H = mol_formula.H + trans_unit.H
                new_O = mol_formula.O + trans_unit.O
                new_N = mol_formula.N + trans_unit.N
                new_S = mol_formula.S + trans_unit.S

                # create dictionary with results
                formula_dict = {
                    'formula_string': mol_formula.formula_string,
                    'transformation_unit': trans_unit.element,
                    'is_addition': 1,
                    'new_C': new_C,
                    'new_H': new_H,
                    'new_O': new_O,
                    'new_N': new_N,
                    'new_S': new_S,
                    'tu_C': trans_unit.C,
                    'tu_H': trans_unit.H,
                    'tu_O': trans_unit.O,
                    'tu_N': trans_unit.N,
                    'tu_S': trans_unit.S
                }
                formula_dict['new_formula'] = create_string_from_calculated_atoms(formula_dict)
                # check if calculated molecule exists in original molecule data
                # see algorithm line 15-17
                if formula_dict['new_formula'] in formula_strings['formula_string'].values:
                    # create strings from atoms of transformation units
                    formula_dict['transformation_unit'] = create_strings_transformation_unit(formula_dict)
                    # append dictionary to list
                    # see algorithm line 18-20
                    formula_list.append(formula_dict)

            # calculate new molecules from given molecules and transformation units in direction: photodegradation
            # choose if transformation unit exist as photo elimination in data
            # see algorithm line 21-22
            if int(trans_unit.minus) == 1:
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
                # see algorithm line 23-25
                new_C = mol_formula.C - trans_unit.C if mol_formula.C - trans_unit.C >= 0 else -1
                if new_C == -1: exist = False
                new_H = mol_formula.H - trans_unit.H if mol_formula.H - trans_unit.H >= 0 else -1
                if new_H == -1: exist = False
                new_O = mol_formula.O - trans_unit.O if mol_formula.O - trans_unit.O >= 0 else -1
                if new_O == -1: exist = False
                new_N = mol_formula.N - trans_unit.N if mol_formula.N - trans_unit.N >= 0 else -1
                if new_N == -1: exist = False
                new_S = mol_formula.S - trans_unit.S if mol_formula.S - trans_unit.S >= 0 else -1
                if new_S == -1: exist = False

                # create dictionary with results
                # only if calculated molecule can exist
                if exist == True:
                    formula_dict = {
                        'formula_string': mol_formula.formula_string,
                        'transformation_unit': trans_unit.element,
                        'is_addition' : 0,
                        'new_C': new_C,
                        'new_H': new_H,
                        'new_O': new_O,
                        'new_N': new_N,
                        'new_S': new_S,
                        'tu_C': (-1)*trans_unit.C if trans_unit.C != 0 else 0,
                        'tu_H': (-1)*trans_unit.H if trans_unit.H != 0 else 0,
                        'tu_O': (-1)*trans_unit.O if trans_unit.O != 0 else 0,
                        'tu_N': (-1)*trans_unit.N if trans_unit.N != 0 else 0,
                        'tu_S': (-1)*trans_unit.S if trans_unit.S != 0 else 0
                    }
                    formula_dict['new_formula'] = create_string_from_calculated_atoms(formula_dict)
                    # check if calculated molecule exists in original molecule data
                    # see algorithm line 26-28
                    if formula_dict['new_formula'] in formula_strings['formula_string'].values:
                        # create strings from atoms of transformation units
                        formula_dict['transformation_unit'] = create_strings_transformation_unit(formula_dict)
                        # append dictionary to list
                        # see algorithm line 29-31
                        formula_list.append(formula_dict)

    bar_calculate_relationships.finish()
    molecule_df = pd.DataFrame(formula_list)
    print('done: calculate new molecules photoaddition')
    # see algorithm line 32-33
    return molecule_df

# create strings from calculated atom count
def create_string_from_calculated_atoms(formula_dict):
    
    # take calculated atoms and append to string -> structure: 'CHNOS'
    new_molecule = ''
    if formula_dict['new_C'] > 0: new_molecule = 'C' + str(formula_dict['new_C'])
    if formula_dict['new_H'] > 0: new_molecule = new_molecule + ' H' + str(formula_dict['new_H'])
    if formula_dict['new_N'] > 0: new_molecule = new_molecule + ' N' + str(formula_dict['new_N'])
    if formula_dict['new_O'] > 0: new_molecule = new_molecule + ' O' + str(formula_dict['new_O'])
    if formula_dict['new_S'] > 0: new_molecule = new_molecule + ' S' + str(formula_dict['new_S'])

    return new_molecule

# create strings from atoms of transformation units
def create_strings_transformation_unit(formula_dict):

    tu_string = ""

    if formula_dict['tu_C'] < 0: tu_string = "-" + tu_string + "C" + str(abs(formula_dict['tu_C'])) + " "
    elif formula_dict['tu_C'] > 0: tu_string = tu_string + "C" + str(formula_dict['tu_C']) + " "
    else: tu_string

    if formula_dict['tu_H'] < 0: tu_string = tu_string + "-H" + str(abs(formula_dict['tu_H'])) + " "
    elif formula_dict['tu_H'] > 0: tu_string = tu_string + "H" + str(formula_dict['tu_H']) + " "
    else: tu_string

    if formula_dict['tu_O'] < 0: tu_string = tu_string + "-O" + str(abs(formula_dict['tu_O'])) + " "
    elif formula_dict['tu_O'] > 0: tu_string = tu_string + "O" + str(formula_dict['tu_O']) + " "
    else: tu_string

    if formula_dict['tu_N'] < 0: tu_string = tu_string + "-N" + str(abs(formula_dict['tu_N'])) + " "
    elif formula_dict['tu_N'] > 0: tu_string = tu_string + "N" + str(formula_dict['tu_N']) + " "
    else: tu_string

    if formula_dict['tu_S'] < 0: tu_string = tu_string + "-S" + str(abs(formula_dict['tu_S'])) + " "
    elif formula_dict['tu_S'] > 0: tu_string = tu_string + "S" + str(formula_dict['tu_S']) + " "
    else: tu_string

    tu_string = tu_string.rstrip()

    return tu_string

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':

    # define data
    formula_strings = pvp.load_csv(pvp.unique_molecules, seperator=[',', ';'])
    transformation_unit = pvp.load_csv(pvp.file_transformation_units, seperator=[',', ';'])

    # calculate
    calculated_relationships = calculate_formula_relationships(formula_strings, transformation_unit)

    #export
    pvp.export_csv(pvp.relationships, calculated_relationships)