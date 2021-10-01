# requirements 

Contains instructions for the Neo4j Desktop setup.  
Contains also bash script to install required libraries.  
  
Owner: Philipp Plamper  
Date: 11. may 2021

## instructions for setup Neo4j Desktop (tested on Linux)

1. Download a copy of [Neo4j Desktop](https://neo4j.com/download-center/#desktop)
2. Run Neo4j Desktop
3. Create a new project
4. Add with "Add Database" a new local database (database Version 4.1.5 is supported, see [py2neo docs](https://py2neo.org/2020.1/)) and confirm with "Create"
5. Install with "Add Plugin" the plugin "APOC"
- if the installation doesn't work install plugin manually
- open "/plugins" folder of neo4j instance
- drag and drop plugins from project directory "/used_plugins" to "/plugins" folder of neo4j instance
6. Click on the three dots next to your database -> Manage -> Settings 
7. Search for the line "dbms.directories.import=import" and comment it out with "#", then "Apply" (change also [memory settings](https://neo4j.com/developer/guide-performance-tuning/) if needed)
- only necessary if automatic plugin installation doesn't work
- change line "dbms.security.procedures.unrestricted=jwt.security.*" to "dbms.security.procedures.unrestricted=jwt.security.*,apoc.*"
8. Go back and start the database
9. Click on the three dots next to your database -> Manage -> Details -> copy the HTTP port for later
10. Go back and open the "Neo4j Browser" with "Open" for later
11. Go into your IDE and change the settings of the "create_models/create_" scripts (at minimum port and credentials)
12. Run the script
13. Go into your "Neo4j Browser" 
14. Under "Use Database" search for given name in script settings
15. done

## instructions for setup Python (tested on Linux)

- use Python 3 to run the scripts
- make sure you have pip installed
- install used libraries 
    - from command line with "[python3 -m] pip install -r PATH/TO/REQUIREMENTS/requirements.txt"
    - or run bash script "install_requirements.sh" (maybe you have to add permission)