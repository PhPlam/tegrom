#!/bin/bash

# Name: Philipp Plamper
# Date: 20. september 2022

# create parallel model in neo4j
python C021_create_temporal_graph.py
# create weights of relationships
python C022_add_edge_properties.py
# calculate possible molecule transformations
python C031_predict_transformations.py
# create smashed representation of graph
python C041_smash_graph.py