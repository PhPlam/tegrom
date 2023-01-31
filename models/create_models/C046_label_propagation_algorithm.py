# Name: Philipp Plamper 
# Date: 31. january 2023

from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or delete graph projection for graph catalog
# https://neo4j.com/docs/graph-data-science/current/management-ops/graph-catalog-ops/
def create_delete_projection(session_light, query_params):
    if session_light.run("CALL gds.graph.exists('graphprojection') YIELD exists").single()['exists'] == False:
        session_light.run(
            "CALL gds.graph.project("
            "'graphprojection', "
            "'" + query_params['label_node'] + "', "
            "{" + query_params['label_chemical_edge'] + ": {orientation: 'NATURAL'}}, "
            "{relationshipProperties: '" + query_params['prop_extra_9'] + "'}) "
            "YIELD graphName"
        )
        print('done: create graph projection')
    else:
        session_light.run(
            "CALL gds.graph.drop('graphprojection') "
            "YIELD graphName"
        ) 
        print('done: delete graph projection')


# run label propagation algorithm 
# https://neo4j.com/docs/graph-data-science/current/algorithms/label-propagation/
def label_propagation_algorithm(session_light, query_params):
    session_light.run(
        "CALL gds.labelPropagation.write('graphprojection', "
        "{relationshipWeightProperty: '" + query_params['prop_extra_9'] + "', writeProperty: 'community'})"
    )
    print('done: run label propagation algorithm')

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create connection to light temporal graph
    session_light = pvc.pf.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_light)

    # create graph projection
    create_delete_projection(session_light, pvc.query_params)

    # run label propagation
    label_propagation_algorithm(session_light, pvc.query_params)

    # delete graph projection
    create_delete_projection(session_light, pvc.query_params)

    # close sessions
    session_light.close()
