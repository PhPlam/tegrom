#!/bin/bash

# Name: Philipp Plamper
# Date: 11. may 2021

# create parallel model in neo4j
python C020_create_parallel_model.py
# create weights of relationships
python C022_create_tendency_weights_new.py
# calculate possible molecule transformations (see concept)
python C030_calculate_possible_transformations.py