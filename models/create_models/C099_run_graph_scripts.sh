#!/bin/bash

# Name: Philipp Plamper
# Date: 31. january 2023

# create parallel model in neo4j
python C021_create_temporal_graph.py

# calculate possible molecule transformations
python C031_predict_transformations.py

# create weights of relationships
python C036_add_weights.py

# create light representation of temporal graph
python C041_create_light_graph.py

# run label propgation algorithm
python C046_label_propagation_algorithm.py