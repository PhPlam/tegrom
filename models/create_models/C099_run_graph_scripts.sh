#!/bin/bash

# Name: Philipp Plamper
# Date: 23. january 2023

# create parallel model in neo4j
python C021_create_temporal_graph.py

# calculate possible molecule transformations
python C031_predict_transformations.py

# create weights of relationships
python C036_add_weights.py

# create smashed representation of graph
python C041_create_light_graph.py