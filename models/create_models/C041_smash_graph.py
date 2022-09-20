# Name: Philipp Plamper 
# Date: 20. september 2022

from py2neo import Graph
from C000_path_variables_create import host, user, passwd, db_name_temporal, db_name_smash


##################################################################################
#settings#########################################################################
##################################################################################

# credentials 
host = host
user = user
passwd = passwd

# select database
db_name = db_name_temporal
db_name_smash = db_name_smash


##################################################################################
#define functions to create the graph#############################################
##################################################################################

# create or replace database based on 'db_name' in neo4j instance with help of the initial 'system' database
def create_database(host, user, passwd, db_name_smash): 
    system_db = Graph(host, auth=(user, passwd), name='system')
    system_db.run("CREATE OR REPLACE DATABASE " + db_name_smash)
    print('done: create or replace database')


# establish connection to the new or replaced database based on 'db_name'
def get_database_connection(host, user, passwd, db_name):
    database_connection = Graph(host, auth=(user, passwd), name=db_name)
    print('done: establish database connection')
    return database_connection


# deal with not existing "SAME_AS" relationships
# get all pot relationships
def get_relationships(call_graph):
    new_model_paths = call_graph.run("""
        MATCH (m1:Molecule)-[p:POTENTIAL_TRANSFORMATION]->(m2:Molecule)
        OPTIONAL MATCH (m1)-[s1:SAME_AS]->(:Molecule)
        OPTIONAL MATCH (:Molecule)-[s2:SAME_AS]->(m2)
        WHERE m2.point_in_time = m1.point_in_time + 1
        RETURN m1.formula_string as mol_from, m1.peak_relint_tic as mol_from_int, m1.point_in_time as mol_from_time, 
        s1.intensity_trend as mol_from_int_trend, m2.formula_string as mol_to, m2.peak_relint_tic as mol_to_int, 
        m2.point_in_time as mol_to_time, s2.intensity_trend as mol_to_int_trend, p.tu_pot as transformation_unit 
    """).to_data_frame()

    # fill null values of columns matched with 'Optional Match'
    new_model_paths = new_model_paths.fillna(0)

    print('done: get all potential transformation relationships')

    return new_model_paths


# create molecule nodes from unique formula strings
def create_nodes_molecule(call_graph_par, call_graph_com):
    df_unique_mol = call_graph_par.run("""
    MATCH (m:Molecule)
    RETURN m.formula_string as formula_string, 
        m.C as C, m.H as H, m.O as O, m.N as N, m.S as S, 
        m.formula_class as formula_class, 
        toFloat(m.O)/toFloat(m.C) as OC, 
        toFloat(m.H)/toFloat(m.C) as HC,
        count(m) as cnt 
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_unique_mol.iterrows():
        tx.evaluate("""
            CREATE (:Molecule {formula_string:$formula_string,         
                    C : toInteger($C), 
                    H : toInteger($H), 
                    O : toInteger($O), 
                    N : toInteger($N), 
                    S : toInteger($S),
                    formula_class : $formula_class,
                    OC : toFloat($O)/toFloat($C),
                    HC : toFloat($H)/toFloat($C)})
            RETURN count(*) 
        """, parameters= {'formula_string': row['formula_string'], 'C': row['C'], 
        'H': row['H'], 'O': row['O'], 'N': row['N'], 'S': row['S'], 
        'formula_class': row['formula_class']})
    call_graph_com.commit(tx)

    print('done: create nodes molecule')


# create index on formula string
def create_index(call_graph):
    call_graph.run("CREATE INDEX FOR (m:Molecule) ON (m.formula_string)")

    print('done: create index on formula string')


# create CHEMICAL_TRANSFORMATION relationship
def create_relationship_chemical_transformation(call_graph_par, call_graph_com):
    df_pot_rel = call_graph_par.run("""
    MATCH (m1:Molecule)-[pot:POTENTIAL_TRANSFORMATION]->(m2:Molecule)
    RETURN  m1.formula_string as from_fs, pot.tu_pot as tu, 
        m2.formula_string as to_fs, pot.C as C, pot.H as H, 
        pot.O as O, pot.N as N, pot.S as S, count(*)
    """).to_data_frame()

    tx = call_graph_com.begin()
    for index, row in df_pot_rel.iterrows():
        tx.evaluate("""
            MATCH (m1:Molecule), (m2:Molecule)
            WHERE m1.formula_string = $from_fs 
                AND m2.formula_string = $to_fs
            CREATE (m1)-[:CHEMICAL_TRANSFORMATION {tu: $tu, C:$C, H: $H, O: $O, N: $N, S: $S}]->(m2)
            RETURN count(*)
        """, parameters= {'from_fs': row['from_fs'], 'to_fs': row['to_fs'], 'C': row['C'], 
        'H': row['H'], 'O': row['O'], 'N': row['N'], 'S': row['S'], 'tu': row['tu']}
        )
    call_graph_com.commit(tx)

    print('done: create relationship chemical transformation')


# create and set properties at relationship CHEMICAL_TRANSRFORMATION
def set_properties_chemical_transformation(call_graph_com, new_model_paths):
    for i in range (1,new_model_paths.mol_to_time.max()+1):
        is_prt_list = []
        new_model_paths_trim = new_model_paths[new_model_paths.mol_to_time == i]
        
        for row in new_model_paths_trim.itertuples():
            if 0 < row.mol_from_int_trend < 0.975 and row.mol_to_int_trend > 1.025:
                is_prt_list.append(1)
            else:
                is_prt_list.append(0)
        new_model_paths_trim['is_prt'] = is_prt_list

        tx = call_graph_com.begin()
        for index, row in new_model_paths_trim.iterrows():
            tx.evaluate("""
                MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(m2:Molecule)
                WHERE m1.formula_string = $mol_from
                    AND m2.formula_string = $mol_to
                    AND c.tu = $transformation_unit
                SET c.transition_""" + str(i) + """ = [toFloat($mol_to_time), toFloat($mol_from_int), 
                    toFloat($mol_to_int), toFloat($mol_from_int_trend), 
                    toFloat($mol_to_int_trend), toFloat($is_prt)]        
            """, parameters= {'mol_from': row.mol_from, 'mol_to': row.mol_to, 'transformation_unit': row.transformation_unit,
            'mol_to_time': row.mol_to_time, 'mol_from_int': row.mol_from_int, 'mol_to_int': row.mol_to_int,
            'mol_from_int_trend': row.mol_from_int_trend, 'mol_to_int_trend': row.mol_to_int_trend,
            'is_prt': row.is_prt}
            )
        call_graph_com.commit(tx)
        print('done: set properties of transition:', str(i))
    
    print('done: set properties at relationship chemical transformation')
        
    # order of properties in List
    # 1. transition
    # 2. relative intensity of source molecule
    # 3. relative intensity of target molecule
    # 4. intensity trend to molecule with same formula of source molecule
    # 5. intensity trend from molecule with same formula of target molecule
    # 6. is prt, see RelIdent-algorithm


# property 'transition_count'
# = number of transtions between two molecules 
def create_property_transition_count(call_graph):
    call_graph.run("""
        MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
        WITH m1, c, size(keys(c))-6 as keys
        SET c.transition_count = keys
        RETURN m1.formula_string, keys LIMIT 5
    """)

    print('done: create property transition count')


# property 'prt_count'
# = number of transtions recognizes as edge of type 'prt' 
def create_property_prt_count(call_graph, new_model_paths):
    call_graph.run("""
        MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
        SET c.prt_count = 0
        RETURN count(*)
    """)

    for i in range(1,new_model_paths.mol_to_time.max()+1):
        call_graph.run("""
            MATCH (m1:Molecule)-[c:CHEMICAL_TRANSFORMATION]->(:Molecule)
            WHERE c.transition_""" + str(i) + """[5] = 1
            SET c.prt_count = c.prt_count + 1
            RETURN count(*)
        """)

    print('done: create property prt count')


##################################################################################
#call functions###################################################################
##################################################################################

# create database and establish connection
create_database(host, user, passwd, db_name_smash)


# connect to parallel model
call_graph_par = get_database_connection(host, user, passwd, db_name)
new_model_paths = get_relationships(call_graph_par)


# connect to compact model
call_graph_com = get_database_connection(host, user, passwd, db_name_smash)
create_nodes_molecule(call_graph_par, call_graph_com)
create_index(call_graph_com)
create_relationship_chemical_transformation(call_graph_par, call_graph_com)
set_properties_chemical_transformation(call_graph_com, new_model_paths)
create_property_transition_count(call_graph_com)
create_property_prt_count(call_graph_com, new_model_paths)