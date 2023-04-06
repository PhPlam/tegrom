#!/bin/bash

# Name: Philipp Plamper
# Date: 06. april 2023

# create parallel model in neo4j
python3 C021_create_temporal_graph.py

# calculate possible molecule transformations
python3 C031_predict_transformations.py

# create weights of relationships
python3 C036_add_weights.py

# create light representation of temporal graph
python3 C041_create_light_graph.py

# run label propgation algorithm
python3 C046_label_propagation_algorithm.py