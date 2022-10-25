# Name: Philipp Plamper
# Date: 25. october 2022

import unittest

target = __import__('create_models.py')
database_connection = target.get_database_connection()

class TestDatabase(unittest.TestCase()):
    def test_database_connection(self):
        # host + port
        host = 'http://localhost:7474'

        # username and password for neo4j instance
        user = 'neo4j'
        passwd = '1234'

        # names for neo4j databases
        db_name_temporal = 'modeltemporal'
        