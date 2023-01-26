# Name: Philipp Plamper 
# Date: 24. january 2023

import numpy as np
import matplotlib.pyplot as plt

import A000_path_variables_analyze as pva

##################################################################################
#analyze functions################################################################
##################################################################################






##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create session to database and analyze graph
    session = pva.pf.connect_to_database(pva.host, pva.user, pva.passwd, pva.db_name_temporal)
    # add analyze function here
    
    # end session
    session.close()