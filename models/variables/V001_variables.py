# Name: Philipp Plamper
# Date: 02. febraury 2023

### parameter for ###
### database connection ### 

# host + port
host = 'bolt://localhost:7687' # default: bolt://localhost:7687

# username and password for neo4j instance
user = 'neo4j' # default: neo4j
passwd = 'test1234' # default: neo4j or 1234 or test1234

# names for neo4j databases
db_name_temporal = 'modeltemporal' # name of temporal graph
db_name_light = 'modellightprt' # name of smashed graph
#db_name_rev = 'modeltransformback' # for testing; name of reverted graph
# db_name_rev from test: can the smashed graph be converted back to the temporal graph

# define threshold for intensity trend 
upper_limit = 1.025 # above considered as increasing intensity
lower_limit = 0.975 # below considered as decreasing intensity


### names of ###
### all files used for model ###
### from UFZ ###

# from UFZ assigned molecular formulas and several properties
file_molecules = 'Philipp - Temporal Graph_formulas.final_new.avg_2023-01-04.csv'

# from UFZ given transformation units
file_transformation_units = 'transformations_handwritten.csv'

# from UFZ metadata of sample
file_sample_meta = 'Photodatensatz_Graphanalyse_sample.metadata_2020-09-10.csv'

# from UFZ metadata of measurements
file_sample_join = 'Photodatensatz_Graphanalyse_meas.metadata_2020-09-10.csv'

### names of ###
### created files ###
### in runtime ### 

# unique molecular formulas of molecules
# no molecule formula appears more than one time
unique_molecules = 'unique_formula_strings.csv'

# cleaned assigned molecular formulas 
# e.g. filled null values, remove molecule formulas with specific atom count
cleaned_molecules = 'ufz_all_formulas_cleaned.csv'

# calculated edges
# contains the possible edges between molecular formulas
# based on transformation units
relationships = 'formula_relationships.csv'

# combined metadata
# combination of metadata from sample and measurement
metadata = 'sample_metadata.csv'

### preprocessing parameters and ###
### Neo4j Query parameters/properties ###

model_params = {
    'label_node' : 'Molecule', # String; label nodes
    'label_same_as' : 'SAME_AS', # String; label edges
    'label_potential_edge' : 'POTENTIAL_TRANSFORMATION', # String; label edges
    'label_predicted_edge' : 'PREDICTED_TRANSFORMATION', # String; label edges
    'label_chemical_edge' : 'CHEMICAL_TRANSFORMATION', # String; label edges
    'prop_node_name' : 'molecular_formula', # property name; String
    'prop_node_value' : 'normalized_intensity', # property value; Float
    'prop_node_snapshot' : 'snapshot', # property time; Integer
    'prop_edge_value_1' : 'transformation_unit', # property name; String
    'prop_edge_value_2' : 'intensity_trend', # property value; Float
    'prop_extra_1' : 'C', # property value; Integer
    'prop_extra_2' : 'H', # property value; Integer
    'prop_extra_3' : 'N', # property value; Integer
    'prop_extra_4' : 'O', # property value; Integer
    'prop_extra_5' : 'S', # property value; Integer
    'prop_extra_8' : 'transition_count', # property value; Integer
    'prop_extra_9' : 'prt_count', # Integer; property value Integer
    'prop_extra_10': 'tendency_weight', # Float; temporal value for weight calculation
    'prop_extra_11': 'predicted_weight', # Float
    'prop_extra_12': 'radiation_dose', # Float
    'prop_extra_13': 'is_addition', # Boolean; 1 if transformation is photo addition
    'prop_extra_14': 'formula_class', # String
    'prop_extra_15': 'normalized_predicted_weight', # Float
    'prop_extra_16': 'formula_mass_nominal', # Integer
    'prop_extra_17': 'average_intensity', # Float
    'prop_extra_18': 'occurrence_count' # Integer
}
