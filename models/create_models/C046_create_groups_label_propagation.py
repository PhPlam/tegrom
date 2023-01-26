# Name: Philipp Plamper 
# Date: 24. january 2023

from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################




##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create database for light temporal graph
    pvc.create_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_light)

    # add functions here

    # close sessions
    session_light.close()
