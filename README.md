# A temporal graph model for environmental data in Neo4j

Authors: Philipp Plamper, Oliver J. Lechtenfeld, Anika Groß  
Date: 20. november 2023  

This project contains our implementation and source code for a snapshot-based knowledge graph model. 
The novel approach is based on a temporal graph and is able to predict interactions between nodes in succeeding snapshots. 
A practical application is already shown in the paper "A temporal graph model to predict chemical transformations in complex dissolved organic matter" (Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß) (https://doi.org/10.1021/acs.est.3c00351)
  
The experimental data from FT-ICR-MS used in this project were originally used in paper "Photochemically Induced Changes of Dissolved Organic Matter in a Humic-Rich and Forested Stream" (Christin Wilske, Peter Herzsprung, Oliver J. Lechtenfeld, Norbert Kamjunke, Wolf von Tümpling) (https://doi.org/10.3390/w12020331) 
  
### Graph Model in chemical application

![graph_model_v4](https://user-images.githubusercontent.com/91727135/223053780-73f2dbd3-be5c-4022-8868-0edfa99d8e7b.png)

# Instructions to set up temporal graph in a Neo4j Desktop instance
tested on Manjaro Linux (20. october 2023)

## Project

### Software Versions

- Neo4j Desktop [Link](https://neo4j.com/download/) 
> Desktop version 1.5.7 (21. april 2023)  
> Database version 5.3.0 (21. april 2023)
- Python version 3.10.9 
- neo4j (Python driver) [Link](https://neo4j.com/docs/api/python-driver/current/)
> version 5.6.0 (21. april 2023) 

### Project structure

- Temporal-Graphs-Neo4j  
  - models
    - analyze
    - create_models
    - data_preprocessing
    - files_for_model
    - variables
  - requirements
  - test
    - notebooks
      - results

### Setup Neo4j Desktop

1. Download and run Neo4j Desktop [Link](https://neo4j.com/download/) 
2. Create a new project (no whitespace or special characters):
   
   ![create_new_project](https://user-images.githubusercontent.com/91727135/227484285-ca96d4a9-2288-4d92-acb8-83bdeff48713.png)
   
3. Go to project and add a new local database
    * Name: e.g. MoleculeGraph
    * Password: e.g. test1234  
    * “Create”
    
    ![add_local_db](https://user-images.githubusercontent.com/91727135/227484203-404f2b6c-9543-4043-87ad-dc966b0aab42.png)
    
4. Allow data from external sources
    * open the settings of the database (three dots on the right side)
    * search for: “dbms.directories.import=import”
        * in newer version: “server.directories.import=import”
    * comment the line with “#”
        * e.g. “#dbms.directories.import=import”
    * “Apply” and “Close”
   
    ![ext_src](https://user-images.githubusercontent.com/91727135/227484243-89dc7648-8f63-460a-9a7c-9e524cb7b9f1.png)

5. Install the APOC and the Graph Data Science Library Plugin
    * Click on the database (a window should appear on the right side)
    * Go to “Plugins” and install APOC and Graph Data Science Library
    
    ![plugins](https://user-images.githubusercontent.com/91727135/227484313-12fae12d-2ed9-4983-bf11-7c99554e5771.png)

6. Start the database

### Requirements 
* install required python libraries
    * they can be found in: “requirements/requirements.txt” (see chapter “Project Structure”)
    * install required libraries (e.g. manually via pip or with command line)
        * command line:  
        $ pip install -r Path/To/requirements.txt

## Temporal graph model

### Prepare dataset

* add data for preprocessing
* add your files to path: “models/files_for_model” (see chapter “Project Structure”)
    * if necessary delete all existing files in folder 
    * molecules and properties 
        * rename to “molecule_formulas.csv”
        * delimiter = ‘,’ or ‘;’
        * requires ascending order of measurements
            * e.g. measurement id 1, measurement id 2, …
        * columns: 
            * “measurement_id” : Integer
            * “peak_relint_tic” (normalized intensity) : Float
            * “formula_mass_nominal” : Integer
            * “formula_string” : String
                * molecular formulas should be in the form CHNOS
                * e.g. “C9 H12 O5”, “C15 H11 N1 O6”, “C16 H14 O9 S1”
            * “C” : Integer
            * “H” : Integer
            * “N” : Integer
            * “O” : Integer
            * “S” : Integer
    * transformation units 
        * rename to “transformations_handwritten.csv”
        * delimiter = ‘,’ or ‘;’
        * columns:
            * “element” : String
            * “C” : Integer
            * “H” : Integer
            * “N” : Integer
            * “O” : Integer
            * “S” : Integer
            * “plus” : Boolean (0,1) → photo addition
            * “minus” : Boolean (0,1) → photo elimination
  
* preprocess data for temporal graph
    * execute Bash script “P099_run_preprocessing_scripts.sh”  
    $ sh models/data_preprocessing/P099_run_preprocessing_scripts.sh

### Create temporal graph

* start scripts to create temporal graph
    * adjust parameters in “models/variables/V001_variables.py”
        * host (default: bolt://localhost:7687) -> see in Neo4j Desktop “Details”
        * user (default: neo4j)
        * passwd -> see “Setup Neo4j Desktop”
        * (optional) db_name -> names for databases
        * (optional) limits -> threshold for intensity trends
    * execute Bash script “C099_run_graph_scripts.sh”  
    $ sh models/create_models/C099_run_graph_scripts.sh

### Analyze graph 

* start scripts to analyze graph
    * execute Bash script “A099_run_analysis.sh”  
    $ sh models/analyze/A099_run_analysis.sh

