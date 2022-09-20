#!/bin/bash

# Name: Philipp Plamper
# Date: 19. september 2022

# create metadata for model
python P005_merge_metadata.py
# clean molecules
python P010_clean_molecule_data.py
# calculate edges pot
python P020_calculate_potential_transformation_relationship.py