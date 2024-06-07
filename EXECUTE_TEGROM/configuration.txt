###parameter for database connection_____________________
host = 'bolt://localhost:7687' # default: bolt://localhost:7687
user = 'neo4j' # default: neo4j
passwd = 'Test1234' # default: Test1234


###names for neo4j databases_____________________________
db_name_temporal = 'modeltemporal' # name of temporal graph
db_name_light = 'modellight' # name of smashed graph

###name of files_________________________________________
# assigned molecular formulas by mass spectrometry
file_molecules = 'molecule_formulas.csv'
# transformation units
file_transformation_units = 'transformations_handwritten.csv'

###threshold for intensity trend_________________________
upper_limit = 0.025 # above considered as increasing intensity, default: 0.025
lower_limit = -0.025 # below considered as decreasing intensity, default: -0.025
