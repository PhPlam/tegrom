# Requirements 

Contains instructions for the Neo4j Desktop setup.  
Contains also bash script to install required libraries.  
  
Owner: Philipp Plamper  
Date: 08. october 2021

## Instructions for setup Neo4j Desktop (tested on Linux)

1. Download a copy of [Neo4j Desktop](https://neo4j.com/download-center/#desktop)
2. Run Neo4j Desktop
3. Create a new project
4. Add with "Add Database" a new local database (database Version 4.3.3 is supported, see [py2neo docs](https://py2neo.org/2020.1/)) and confirm with "Create"
5. Install with "Add Plugin" the plugin "APOC"
6. Click on the three dots next to your database -> Manage -> Settings 
7. Search for the line "dbms.directories.import=import" and comment it out with "#", then "Apply" (change also [memory settings](https://neo4j.com/developer/guide-performance-tuning/) if needed)
8. Go back and start the database
9. Click on the three dots next to your database -> Manage -> Details -> copy the HTTP port
10. Go back and open the "Neo4j Browser" with "Open"
11. Go into your IDE and adjust the settings of the "models/create_models/C000_path_variables_create.py" script (add port and credentials)
12. Check and install the required libraries in "requirements/requirements.txt" 
13. Run the scripts "C020_..., C022_..., C030_..." in "models/create_models/" 
14. Go into your "Neo4j Browser" 
15. Under "Use Database" search for given 'db_name' in script "models/create_models/C000_path_variables_create.py"
16. Done

## Instructions for installing libraries in Python (tested on Linux)

- use Python 3 to run the scripts
- make sure you have pip installed
- install used libraries 
    - from command line with "[python3 -m] pip install -r PATH/TO/REQUIREMENTS/requirements.txt"
    - or run bash script "install_requirements.sh" (maybe you have to add permission)