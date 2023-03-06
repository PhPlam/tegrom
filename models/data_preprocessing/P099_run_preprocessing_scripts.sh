#!/bin/bash

# Name: Philipp Plamper
# Date: 06. march 2023

# create metadata for model
# currently not in use
#python P005_merge_metadata.py

# clean molecules
python P010_clean_molecule_data.py

# calculate edges pot
python P020_calculate_potential_transformation_relationship.py