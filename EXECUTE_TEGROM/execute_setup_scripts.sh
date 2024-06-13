#!/bin/bash

# date: 13. june 2024
# author: Philipp Plamper

# get directories of remote script
DATADIR=${PWD}/data/
CONFFILE=${PWD}/configuration.txt

# get directories of tegrom
PROJECTDIR=${PWD%/*}
PREPROCESSDIR=${PROJECTDIR}/models/data_preprocessing
CREATEDIR=${PROJECTDIR}/models/create_models
ANALYZEDIR=${PROJECTDIR}/models/analyze
FILEDIR=${PROJECTDIR}/models/files_for_model

# copy configuration into project
cp $CONFFILE ${PWD%/*}/models/variables/V003_remote_conf.py
# remove all current files for setup
rm -r ${FILEDIR}/*.* 2> /dev/null
# remove exisitng analyses results
rm -r ${ANALYZEDIR}/analyze_results/*.* 2> /dev/null

# get name of data folder
read -p "name of data directory: " DATA
# copy data to tegrom setup
cp ${DATADIR}${DATA}/* $FILEDIR 2> /dev/null

# ask for light graph
read -p "create also light graph? This increases used time a lot. y/[n] " CONTINUE

# execute data_preprocessing
python ${PREPROCESSDIR}/P010_clean_molecule_data.py
python ${PREPROCESSDIR}/P020_calculate_potential_transformation_relationship.py

# execute create_models
python ${CREATEDIR}/C021_create_temporal_graph.py
python ${CREATEDIR}/C031_predict_transformations.py
python ${CREATEDIR}/C036_add_weights.py

# execute analyze
python ${ANALYZEDIR}/A030_analyze_structure.py
python ${ANALYZEDIR}/A032_development_transformation_units_overall.py
python ${ANALYZEDIR}/A034_development_transformation_unit_single.py
python ${ANALYZEDIR}/A036_weights_transformation_units_overall.py
python ${ANALYZEDIR}/A038_development_photo_processes.py
python ${ANALYZEDIR}/A042_analyze_outdegree.py

# create light graph
if [[ $CONTINUE == 'y' ]];
then
    python ${CREATEDIR}/C041_create_light_graph.py
    python ${CREATEDIR}/C046_label_propagation_algorithm.py
    python ${ANALYZEDIR}/A040_visualize_groups_label_propagation.py
    python ${ANALYZEDIR}/A041_analyze_groups_label_propagation.py
fi

# export results
mkdir ${DATADIR}${DATA}/results 2> /dev/null
cp ${ANALYZEDIR}/analyze_results/*.png ${DATADIR}${DATA}/results

# cleaning steps
# remove all current files for setup
rm -r ${FILEDIR}/*.*
# remove exisitng analyses results
rm -r ${ANALYZEDIR}/analyze_results/*.*
# remove configuration
rm ${PWD%/*}/models/variables/V003_remote_conf.py
