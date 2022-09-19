# Graph analysis

Owner: Philipp Plamper
Date: 19. september 2022

## Function description

### Analyze data

1. molecules_per_measurement()
- bar plot
- displays the molecules per measurement from the given data
- contains also average molecule count, standard deviation and multiple assignments
- x-axis = measurement
- y-axis = number of molecules

2. sum_relative_intensity()
- bar plot
- displays the sum of the relative intensities per measurement (should be 1.0)
- addresses the multiple assignments in the data
- x-axis = measurement
- y-axis = sum of the relative intensities 

3. occurrence_formula_class()
- bar plot
- displays the proportion of the formula classes in the given data
- x-axis = formula class
- y-axis = proportion of the formula class

### analyze graph

1. get_intensity_trend_distribution()
- bar plot
- displays the number of "SAME_AS" relationships per measurement
- contains also the number of nodes "Molecule" per measurement and the distribution of the different intensity trends
- x-axis = measurement
- y-axis = number of "SAME_AS" relationships

2. outgoing_transformations_measurement()
- bar plot
- displays the number of outgoing transformations per measurement
- shows the POTENTIAL_TRANSFORMATION and the HAS_TRANSFORMED_INTO relationships
- contains also the number of nodes "Molecule" per measurement
- x-axis = measurement
- y-axis = number of outgoing transformations

3. outgoing_transformations_occurrence()
- bar plot
- displays the distribution of the number of outgoing transformations per node "Molecule"
- divides between POTENTIAL_TRANSFORMATION and HAS_TRANSFORMED_INTO relationships
- x-axis = number of outgoing transformations
- y-axis = proportion in the graph

4. most_occurring_transformations()
- bar plot
- displays the proportion of the occurring transformations across all measurements
- divides between POTENTIAL_TRANSFORMATION and HAS_TRANSFORMED_INTO relationships
- x-axis = Proportion of transformation
- y-axis = chemical transformation

5. most_occurring_transformations_measurement_bar()
- bar plots
- displays the proportion of the occurring transformations per measurement
- divides between POTENTIAL_TRANSFORMATION and HAS_TRANSFORMED_INTO relationships
- x-axis = Proportion of transformation
- y-axis = chemical transformation
- based on 'most_occurring_transformations()' 
- not working properly

6. most_occurring_transformations_measurement_line()
- line plot
- displays the proportion of the occurring transformations per measurement
- seperate image for POTENTIAL_TRANSFORMATION and HAS_TRANSFORMED_INTO relationships
- x-axis = measurement
- y-axis = proportion of transformation

7. average_weight_transformations_bar()
- bar plot
- displays the average calculated weight of every transformation across all measurements
- divides between combined and connected weight
- x-axis = weight
- y-axis = chemical transformation

8. average_weight_transformations_line()
- line plot
- displays the average calculated weight of every transformation per measurement
- seperate image for combined and connected weight
- x-axis = measurement
- y-axis = average weight