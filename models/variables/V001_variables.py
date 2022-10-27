# Name: Philipp Plamper
# Date: 27. october 2022

### database connection ### 

# host + port
host = 'http://localhost:7474'

# username and password for neo4j instance
user = 'neo4j'
passwd = '1234'

# names for neo4j databases
db_name_temporal = 'modeltemporaltest'
db_name_smash = 'modelsmashprt'
db_name_rev = 'modeltransformback'

# define threshold for intensity trend 
upper_limit = 1.025 # above considered as increasing intensity
lower_limit = 0.975 # below considered as decreasing intensity

### filenames ###

# molecules
file_molecules = 'Photodatensatz_Graphanalyse_formulas_2020-09-10.csv'

# transformation units
file_transformation_units = 'transformations_handwritten.csv'

# metadata of sample
file_sample_meta = 'Photodatensatz_Graphanalyse_sample.metadata_2020-09-10.csv'

# metadata of measurements
file_sample_join = 'Photodatensatz_Graphanalyse_meas.metadata_2020-09-10.csv'

### paths to export calculated data ### 

# unique formulas of molecules
unique_molecules = 'unique_formula_strings.csv'

# cleaned file with molecules (e.g. filled null values)
cleaned_molecules = 'ufz_all_formulas_cleaned.csv'

# calculated relationships
relationships = 'formula_relationships.csv'

# metadata
metadata = 'sample_metadata.csv'

### preprocessing parameters and ###
### Neo4j Query parameters/properties ###


model_params = {
    'label_node' : 'Molecule',
    'label_same_as' : 'SAME_AS',
    'label_potential_edge' : 'POTENTIAL_TRANSFORMATION',
    'label_predicted_edge' : 'PREDICTED_TRANSFORMATION',
    'prop_node_name' : 'molecular_formula',
    'prop_node_value' : 'normalized_intensity',
    'prop_node_snapshot' : 'snapshot',
    'prop_edge_value_1' : 'transformation_unit',
    'prop_edge_value_2' : 'intensity_trend',
    'prop_extra_1' : 'C',
    'prop_extra_2' : 'H',
    'prop_extra_3' : 'N',
    'prop_extra_4' : 'O',
    'prop_extra_5' : 'S',
    'prop_extra_6' : 'OC',
    'prop_extra_7' : 'HC'
}