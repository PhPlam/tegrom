# Data preprocessing

contains scripts for preprocessing the data

Owner: Philipp Plamper
Date: 18. october 2021

## New functions

1. remove_measurements()
- define a list of measurements will be removed in the metadata

2. remove_molecules()
- remove molecules in the data with a lower specific atom count than defined

3. remove_molecules_without_measurement()
- remove molecules of the removed measurements based on the metadata
- see remove_measurements()