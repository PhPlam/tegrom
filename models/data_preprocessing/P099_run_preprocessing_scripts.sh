#!/bin/bash

# Name: Philipp Plamper
# Date: 06. april 2023

# create metadata for model
# currently not in use
#python3 P005_merge_metadata.py

# clean molecules
python3 P010_clean_molecule_data.py

# calculate edges pot
python3 P020_calculate_potential_transformation_relationship.py