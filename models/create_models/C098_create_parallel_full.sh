#!/bin/bash

# Name: Philipp Plamper
# Date: 23. june 2022

# create parallel model in neo4j
python C021_create_parallel_model.py
# create weights of relationships
python C022_create_tendency_weights.py
# calculate possible molecule transformations (see concept)
python C031_calculate_possible_transformations.py