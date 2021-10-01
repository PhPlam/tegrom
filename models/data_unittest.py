# Name: Philipp Plamper
# Date: 19. january 2021

# contains unittests 

import unittest
from data_preprocessing.P000_path_variables_preprocess import testPhoto, testUnique, testFunctional, testMeta, testJoin
from create_models.C000_path_variables_create import testSample, testRelationships, testDbConnection, testIntensityCSV, testWeightCSV


##################################################################################
#write unittest###################################################################
##################################################################################

# tests to check existence of files and their columns
# test to check if db connection exists

class testData(unittest.TestCase):
    
    def testPhotoExistence(self):
        print('test file with all formulas')
        self.assertIn('formula_string', testPhoto())
        self.assertIn('formula_class', testPhoto())
        self.assertIn('C', testPhoto())
        self.assertIn('H', testPhoto())
        self.assertIn('O', testPhoto())
        self.assertIn('N', testPhoto())
        self.assertIn('S', testPhoto())
        self.assertIn('peak_relint_tic', testPhoto())

    def testUniqueExistence(self):
        print('test file with unique formula strings')
        self.assertIn('C', testUnique())
        self.assertIn('H', testUnique())
        self.assertIn('O', testUnique())
        self.assertIn('N', testUnique())
        self.assertIn('S', testUnique())
        self.assertIn('formula_string', testUnique())

    def testFunctionalExistence(self):
        print('test file with transformations')
        self.assertIn('C', testFunctional())
        self.assertIn('H', testFunctional())
        self.assertIn('O', testFunctional())
        self.assertIn('N', testFunctional())
        self.assertIn('S', testFunctional())
        self.assertIn('element', testFunctional())
    
    def testSampleExistence(self):
        print('test file with measurement meta data')
        self.assertIn('measurement_id', testSample())
        self.assertIn('sample_id', testSample())
        self.assertIn('radiation_dose', testSample())
        self.assertIn('timepoint', testSample())
        self.assertIn('time', testSample())

    def testRelationshipsExistence(self):
        print('test file with formula relationships')
        self.assertIn('formula_string', testRelationships())
        self.assertIn('new_formula', testRelationships())
        self.assertIn('fg_C', testRelationships())
        self.assertIn('fg_H', testRelationships())
        self.assertIn('fg_O', testRelationships())
        self.assertIn('fg_N', testRelationships())
        self.assertIn('fg_S', testRelationships())

    def testMetaExistence(self):
        print('test file with metadata')
        self.assertIn('sample_id', testMeta())
        self.assertIn('description', testMeta())

    def testJoinExistence(self):
        print('test file with join data')
        self.assertIn('sample_id', testJoin())
        self.assertIn('measurement_id', testJoin())

    def testIntensityCSVExistence(self):
        print('test file with intensity changes')
        self.assertIn('to_molecule', testIntensityCSV())
        self.assertIn('from_mid', testIntensityCSV())
        self.assertIn('to_mid', testIntensityCSV())
        self.assertIn('from_molecule', testIntensityCSV())
        self.assertIn('C', testIntensityCSV())
        self.assertIn('H', testIntensityCSV())
        self.assertIn('O', testIntensityCSV())
        self.assertIn('N', testIntensityCSV())
        self.assertIn('S', testIntensityCSV())
        self.assertIn('tendency_weight_lose', testIntensityCSV())
        self.assertIn('tendency_weight_gain', testIntensityCSV())
        self.assertIn('tendency_weight_combined', testIntensityCSV())
        self.assertIn('fg_group', testIntensityCSV())

    def testWeightCSVExistence(self):
        print('test file with tendency weights')
        self.assertIn('from_formula', testWeightCSV())
        self.assertIn('from_mid', testWeightCSV())
        self.assertIn('to_formula', testWeightCSV())
        self.assertIn('to_mid', testWeightCSV())
        self.assertIn('intensity_trend', testWeightCSV())
        self.assertIn('tendency_weight', testWeightCSV())
        
    def testDbConnection(self):
        print('test DB Connection')
        self.assertEqual(testDbConnection(), 'works')

if __name__ == "__main__":
    unittest.main()