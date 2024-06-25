# Instruction to start Tegrom
Date: 25. june 2024  
author: Philipp Plamper

## General
- you are in the correct directory to start tegrom
- besides this file you should see:
    - directory 'data'
    - file 'configuration.txt'
    - file 'execute_setup_scripts.sh'
- the next three steps describe how you can use tegrom with your data

## Step 1: Data
- create a folder in the directory 'data' (avoid whitespaces and special characters)
    - see folder 'example_dataset' in 'data' as an example
- place your molecular data from mass spectrometry in the created folder
    - see file 'molecule_formulas.csv' in 'example_dataset' as an example
- place your considered chemical transformations in the same directory
    - see file 'transformations_handwritten' in 'example_dataset' as an example

## Step 2: Configuration
- open the file 'configuration.txt' 
- change the name of the temporal database at 'db_name_temporal'
    - this is the final name of the database inside neo4j
    - choose a name that reflects the data/sample/project
    - fist character ASCII alphabetic character, subsequent ASCII alphabetic or numeric characters (no whitespace, no special characters, no underscores)
- change the name of the molecule data at 'file_molecules'
    - it must be the same name as the molecular data in step 1
- change the name of the considered transformation data at 'file_transformation_units'
    - it must be the same name as the chemical transformation data in step 1

## Step 3: Start Tegrom
- execute the script 'execute_setup_scripts.sh'
    - in linux: ```$ bash execute_setup_scripts.sh``` 
    - in windows: ```todo```
- the script asks you for the location of the data, use the name of the folder created in step 1 
- The script then asks you whether you also want to create the light graph. The default value is no.  
    - Only choose yes if you know what you are doing

## Step 4: Get results
- when the execution is complete, the results are saved in the folder created in step 1.