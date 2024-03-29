# Name: Philipp Plamper 
# Date: 27.october 2022

import os
from py2neo import Graph
import C000_path_variables_create as pvc

##################################################################################
#functions########################################################################
##################################################################################

# create index on formula string and point in time
def create_index(call_graph):
    call_graph.run("CREATE INDEX FOR (m:Molecule) ON (m.molecular_formula, m.point_in_time)")

    print('done: create index on formula string and point in time')


def get_molecules(call_graph, transition):
    graph = call_graph
    transition = str(transition)

    molecules = graph.run("""
        MATCH (m1:Molecule)-[ct:CHEMICAL_TRANSFORMATION]->(m2:Molecule)
        WHERE ct.transition_""" + transition + """ IS NOT NULL
        RETURN m1.molecular_formula as from_fs, m1.C as from_C, m1.H as from_H, m1.O as from_O, m1.N as from_N, m1.S as from_S,
            m1.formula_class as from_fc, m2.formula_class as to_fc, m1.OC as from_OC, m2.OC as to_OC, m1.HC as from_HC, m2.HC as to_HC,
            ct.tu as tu, ct.C as tu_C, ct.H as tu_H, ct.O as tu_O, ct.N as tu_N, ct.S as tu_S,
            m2.molecular_formula as to_fs, m2.C as to_C, m2.H as to_H, m2.O as to_O, m2.N as to_N, m2.S as to_S,
            ct.transition_""" + transition + """[1] as from_int, ct.transition_""" + transition + """[2] as to_int, 
            toInteger(ct.transition_""" + transition + """[0]-1) as from_pit, toInteger(ct.transition_""" + transition + """[0]) as to_pit, 
            toInteger(ct.transition_""" + transition + """[5]) as is_prt, ct.transition_""" + transition + """[3] as from_sa, 
            ct.transition_""" + transition + """[4] as to_sa
    """).to_data_frame()
    
    return molecules


# create molecules that are starting point of a chemical transformation 
def merge_molecules_from(call_graph, molecules):
    graph = call_graph
    molecules = molecules

    molecules = molecules.drop_duplicates('from_fs', keep='first')

    tx = graph.begin()
    for index, row in molecules.iterrows():
         tx.evaluate("""
            MERGE (:Molecule {molecular_formula : $molecular_formula,         
                        C : toInteger($C), 
                        H : toInteger($H), 
                        O : toInteger($O), 
                        N : toInteger($N), 
                        S : toInteger($S),
                        //formula_class : $formula_class,
                        OC : toFloat($O)/toFloat($C),
                        HC : toFloat($H)/toFloat($C),
                        peak_relint_tic: toFloat($peak_relint_tic),
                        point_in_time: toInteger($point_in_time)})
            RETURN count(*) 
        """, parameters= {'molecular_formula': row['from_fs'], 'C': row['from_C'], 
        'H': row['from_H'], 'O': row['from_O'], 'N': row['from_N'], 'S': row['from_S'], 
        'formula_class': row['from_fc'], 'peak_relint_tic': row['from_int'], 
        'point_in_time': row['from_pit']})
    graph.commit(tx)


# create molecules that are endpoint of a chemical transformation 
def merge_molecules_to(call_graph, molecules):
    graph = call_graph
    molecules = molecules

    molecules = molecules.drop_duplicates('to_fs', keep='first')

    tx = graph.begin()
    for index, row in molecules.iterrows():
        tx.evaluate("""
            MERGE (:Molecule {molecular_formula : $molecular_formula,         
                        C : toInteger($C), 
                        H : toInteger($H), 
                        O : toInteger($O), 
                        N : toInteger($N), 
                        S : toInteger($S),
                        //formula_class : $formula_class,
                        OC : toFloat($O)/toFloat($C),
                        HC : toFloat($H)/toFloat($C),
                        peak_relint_tic: toFloat($peak_relint_tic),
                        point_in_time: toInteger($point_in_time)})
            RETURN count(*) 
        """, parameters= {'molecular_formula': row['to_fs'], 'C': row['to_C'], 
        'H': row['to_H'], 'O': row['to_O'], 'N': row['to_N'], 'S': row['to_S'], 
        'formula_class': row['to_fc'], 'peak_relint_tic': row['to_int'], 
        'point_in_time': row['to_pit']})
    graph.commit(tx)


# create edges of type potential transformation
def create_edges_pot(call_graph, molecules, transition):
    graph = call_graph
    molecules = molecules 
    transition = transition

    tx = graph.begin()
    for index, row in molecules.iterrows():
        tx.evaluate("""
            MATCH (m1:Molecule), (m2:Molecule)
            WHERE m1.molecular_formula = $from_fs
                AND m1.point_in_time = """ + str(transition -1)+ """ 
                AND m2.molecular_formula = $to_fs 
                AND m2.point_in_time = """ + str(transition) + """ 
            CREATE (m1)-[:POTENTIAL_TRANSFORMATION {transformation_unit: $tu,
                        C : toInteger($C), 
                        H : toInteger($H), 
                        O : toInteger($O), 
                        N : toInteger($N), 
                        S : toInteger($S)}]->(m2)
        """, parameters= {'from_fs': row['from_fs'], 'to_fs': row['to_fs'], 'C': row['tu_C'], 
        'H': row['tu_H'], 'O': row['tu_O'], 'N': row['tu_N'], 'S': row['tu_S'], 'tu' : row['tu']})
    graph.commit(tx)


# create edges of type has transformed into
def create_edges_prt(call_graph, molecules, transition):
    graph = call_graph
    molecules = molecules 
    transition = transition

    tx = graph.begin()
    for index, row in molecules.iterrows():
        if row['is_prt'] == 1:
            tx.evaluate("""
                MATCH (m1:Molecule), (m2:Molecule)
                WHERE m1.molecular_formula = $from_fs
                    AND m1.point_in_time = """ + str(transition -1)+ """ 
                    AND m2.molecular_formula = $to_fs 
                    AND m2.point_in_time = """ + str(transition) + """ 
                CREATE (m1)-[:PREDICTED_TRANSFORMATION {transformation_unit: $tu,
                            C : toInteger($C), 
                            H : toInteger($H), 
                            O : toInteger($O), 
                            N : toInteger($N), 
                            S : toInteger($S)}]->(m2)
            """, parameters= {'from_fs': row['from_fs'], 'to_fs': row['to_fs'], 'C': row['tu_C'], 
            'H': row['tu_H'], 'O': row['tu_O'], 'N': row['tu_N'], 'S': row['tu_S'], 'tu' : row['tu']})
    graph.commit(tx)


# create SAME_AS relationship
def create_relationship_same_as(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule), (m2:Molecule)
        WHERE m2.molecular_formula = m1.molecular_formula AND m2.point_in_time = m1.point_in_time + 1
        CREATE (m1)-[:SAME_AS]->(m2)
    """)
    print('done: create SAME_AS relationship')


# create intensity_trend property
def create_property_intensity_trend(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule)-[s:SAME_AS]->(m2:Molecule)
        WITH (m2.peak_relint_tic/m1.peak_relint_tic) as tendency, m1, m2, s
        SET s.intensity_trend = apoc.math.round(tendency, 3)
    """)
    print('done: create property intensity_trend')

##################################################################################
#call#############################################################################
##################################################################################

# create new database for tranformation
pvc.create_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_rev)

# get database connections
call_graph_com = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_smash)
call_graph_back = pvc.connect_to_database(pvc.host, pvc.user, pvc.passwd, pvc.db_name_rev)
create_index(call_graph_back)

for transition in range(1,13):
    molecules = get_molecules(call_graph_com, transition)
    merge_molecules_from(call_graph_back, molecules)
    merge_molecules_to(call_graph_back, molecules)
    create_edges_pot(call_graph_back, molecules, transition)
    create_edges_prt(call_graph_back, molecules, transition)
    print('done: transition', str(transition))

create_relationship_same_as(call_graph_back)
create_property_intensity_trend(call_graph_back)