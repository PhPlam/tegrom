#!/bin/bash

# Name: Philipp Plamper
# Date: 19. september 2022

# create parallel model in neo4j
python P005_merge_metadata.py
# create weights of relationships
python P010_clean_molecule_data.py
# calculate possible molecule transformations
python P020_calculate_potential_transformation_relationship.py