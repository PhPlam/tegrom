# A temporal graph model for environmental data in Neo4j

Owner: Philipp Plamper  
Date: 24. march 2023  
  
This project belongs to the publications in the following paper: "A temporal graph to predict chemical transformations in complex dissolved organic matter" (Philipp Plamper, Oliver J. Lechtenfeld, Peter Herzsprung, Anika Groß)  
  
The scripts contain methods to create a temporal graph from molecule data acquired over several discrete measurements. Additionally, several methods are provided to analyze the created temporal graph.


### Graph Model

![graph_model_v4](https://user-images.githubusercontent.com/91727135/223053780-73f2dbd3-be5c-4022-8868-0edfa99d8e7b.png)

# Instructions to set up temporal graph in a Neo4j Desktop instance
tested on Manjaro Linux (24. march 2023)

## Project

### Software Versions

- Neo4j Desktop [Link](https://neo4j.com/download/) 
> current version 1.5.7 (24. march 2023)
- Python 3.10.6
- neo4j (Python driver) [Link](https://neo4j.com/docs/api/python-driver/current/)
> current version 5.6.0 (24. march 2023) 

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
    * image here
3. Go to project and add a new local database
    * Name: e.g. MoleculeGraph
    * Password: e.g. test1234  
    * “Create”
    * image here
    
4. Allow data from external sources
    * open the settings of the database (three dots on the right side)
    * search for: “dbms.directories.import=import”
        * in newer version: “server.directories.import=import”
    * comment the line with “#”
        * e.g. “#dbms.directories.import=import”
    * “Apply” and “Close”
    * image here 

5. Install the APOC and the Graph Data Science Library Plugin
    * Click on the database (a window should appear on the right side)
    * Go to “Plugins” and install APOC and Graph Data Science Library
    * image here

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

