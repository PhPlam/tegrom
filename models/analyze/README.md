# Data preprocessing

contains scripts to analyze the data and the graph.

Owner: Philipp Plamper
Date: 18. october 2021

## Function description

### Analyze data

1. molecules_per_measurement()
- displays the molecules per measurement from the given data
- contains also average molecule count, standard deviation and multiple assignments
- x-axis = measurement
- y-axis = number of molecules

2. sum_relative_intensity()
- displays the sum of the relative intensities per measurement (should be 1.0)
- addresses the multiple assignments in the data
- x-axis = measurement
- y-axis = sum of the relative intensities 

3. occurrence_formula_class()
- displays the share of the formula classes in the given data
- x-axis = formula class
- y-axis = share of the formula class

### analyze graph

1. get_intensity_trend_distribution()
- displays the number of "SAME_AS" relationships per measurement
- contains also the number of nodes "Molecule" per measurement and the distribution of the different intensity trends
- x-axis = measurement
- y-axis = number of "SAME_AS" relationships

2. outgoing_transformations_measurement()
- displays the number of outgoing transformations per measurement
- shows the POTENTIAL_TRANSFORMATION and the HAS_TRANSFORMED_INTO relationships
- contains also the number of nodes "Molecule" per measurement
- x-axis = measurement
- y-axis = number of outgoing transformations

3. outgoing_transformations_occurrence()
- displays the distribution of the number of outgoing transformations per node "Molecule"
- divides between POTENTIAL_TRANSFORMATION and HAS_TRANSFORMED_INTO relationships
- x-axis = number of outgoing transformations
- y-axis = share in the graph

4. most_occurring_transformations()

5. most_occurring_transformations_measurement_bar()

6. most_occurring_transformations_measurement_line()

7. average_weight_transformations_bar()

8. average_weight_transformations_line()