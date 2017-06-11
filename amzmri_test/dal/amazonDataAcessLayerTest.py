'''
Created on 9 Aug 2016

@author: sergeykucher
'''
import unittest
from amzmri.dal.amazonDataAccessLayer import AmazonDataAccessLayer

class AmazonDataAccessLayerTest(unittest.TestCase):

    def test_searchFirstNAsins(self):
        dal = AmazonDataAccessLayer()
        lasins = dal.searchFirstNAsins("Portable diaper changing pad", 25)
        self.assertEqual(25, len(lasins))
        print lasins

    def test_get_is_indexed_for_words(self):
        dal = AmazonDataAccessLayer()
        res = dal.get_is_indexed_for_words('B01ETRM2LO', set(['bambi', 'diaper']))
        self.assertEqual({'bambi': False, 'diaper': True}, res)
        
    def test_getProductsByAsins(self):
        dal = AmazonDataAccessLayer()
        expectedAsins = ['B0038JE3R6', 'B0145QF41E', 'B00B7XUVOE']
        products = dal.getProductsByAsins(expectedAsins)        
        self.assertTrue(len(expectedAsins), len(products))
        
        actualAsins = set([p.asin for p in products])
        
        for expectedAsin in expectedAsins:
            self.assertTrue(expectedAsin in actualAsins)
            
            
    def test_getRankForAsins(self):
        dal = AmazonDataAccessLayer()
        expectedAsins = ['B0038JE3R6', 'B0145QF41E', 'B00B7XUVOE']
        products = dal.getRankForAsins(expectedAsins)        
        self.assertTrue(len(expectedAsins), len(products))
        print products
        
    def test_getStockForAsins(self):
        dal = AmazonDataAccessLayer()
        expectedAsins = ['B00B7XUVOE']
        products = dal.getStockForAsins(expectedAsins)        
        self.assertTrue(len(expectedAsins), len(products))
        print products        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_Search']
    unittest.main()