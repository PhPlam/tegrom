# Name: Philipp Plamper 
# Date: 24.march 2023

from neo4j import GraphDatabase
import C000_path_variables_create as pvc

##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or delete graph projection for graph catalog
# https://neo4j.com/docs/graph-data-science/current/management-ops/graph-catalog-ops/
def create_delete_projection(session_temporal, query_params):
    if session_temporal.run("CALL gds.graph.exists('graphprojection') YIELD exists").single()['exists'] == False:
        session_temporal.run(
            "CALL gds.graph.project("
            "'graphprojection', "
            "'" + query_params['nodes_light'].replace(':','') + "', "
            "{" + query_params['label_chemical_edge'] + ": {orientation: 'NATURAL'}}, "
            "{relationshipProperties: '" + query_params['prop_extra_9'] + "'}) "
            "YIELD graphName"
        )
        print('done: create graph projection')
    else:
        session_temporal.run(
            "CALL gds.graph.drop('graphprojection') "
            "YIELD graphName"
        ) 
        print('done: delete graph projection')


# run label propagation algorithm 
# https://neo4j.com/docs/graph-data-science/current/algorithms/label-propagation/
def label_propagation_algorithm(session_temporal, query_params):
    session_temporal.run(
        "CALL gds.labelPropagation.write('graphprojection', "
        "{relationshipWeightProperty: '" + query_params['prop_extra_9'] + "', writeProperty: 'community_lpa'})"
    )
    print('done: run label propagation algorithm')

##################################################################################
#call functions###################################################################
##################################################################################

if __name__ == '__main__':
    # create connection to light temporal graph
    session_temporal = pvc.pf.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_temporal)

    # create graph projection
    create_delete_projection(session_temporal, pvc.query_params)

    # run label propagation
    label_propagation_algorithm(session_temporal, pvc.query_params)

    # delete graph projection
    create_delete_projection(session_temporal, pvc.query_params)

    # close sessions
    session_temporal.close()
