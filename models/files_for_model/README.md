# Used Files

Contains the used files to create the graph.

Name: Philipp Plamper  
Owner: Helmholtz-Zentrum für Umweltforschung UFZ  
Date: 19. september 2022


## File descriptions
  
Informs about content and origin of the used files.


### Given files

1. ufz_all_formulas_raw.csv / Photodatensatz_Graphanalyse_formulas_2020-09-10.csv
- contains all information about the molecules in the dataset 
- from the original ufz dataset

2. transformations_handwritten.csv
- contains necessary information about the transformation units that could possibly occur in the sample
- created by expert (ufz dataset)

3. ufz_sample_meta_raw.csv / Photodatensatz_Graphanalyse_sample.metadata_2020-09-10.csv
- contains metadata
- from the original ufz dataset

4. ufz_sample_join_raw.csv / Photodatensatz_Graphanalyse_meas.metadata_2020-09-10.csv
- contains mapping (sampleID <-> measurementID)
- from the original ufz dataset


### Data preprocessing

5. ufz_all_formulas_cleaned.csv
- filled null values in table
- derived from (1.) and calculated in data_preprocessing
- used for nodes Molecule

6. unique_formula_strings.csv
- contains unique formula strings of molecules, duplicates are removed
- derived from (1.) and calculated in data_preprocessing

7. formula_relationships.csv
- calculated possible transformations in the graph  
- derived from (2.) and (6.) and calculated in data_preprocessing
- used for relationship POTENTIAL_TRANSFORMATION

8. sample_metadata.csv
- contains mapped IDs and metadata
- derived from (3.) and (4.) and calculated in data_preprocessing
- used for nodes Measurement


### Runtime files

9. tendency_weights.csv
- contains calculated tendency weights
- calculated at runtime
- used for property tendency_weight

10. increasing_intensities.csv
- contains results of RelIdent-Algorithm (occuring transformations between points in time)
- calculated at runtime
- used for relationship HAS_TRANSFORMED_INTO
- used for property combined/connected weight
