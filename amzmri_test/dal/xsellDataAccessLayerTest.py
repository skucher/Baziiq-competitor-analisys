'''
Created on 10 Aug 2016

@author: sergeykucher
'''
import unittest
from google.appengine.ext import testbed, ndb
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
from amzmri.dal.tables.bsr import Bsr
import datetime
from amzmri.dal.tables.keywordRank import KeywordRank


class XSellDataAccessLayerTest(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def testPutBsrs(self):
        dal = XSellDataAccessLayer()
        lAsinBsrs = [('abc', 1234), ('cde', 1)]
        dal.storeBsrs(lAsinBsrs)
        query = Bsr.query().filter(Bsr.asin == 'abc')
        results = query.fetch()
        self.assertEqual(1, len(results))
        self.assertEqual(1234, results[0].bsr)
        
        query = Bsr.query().filter(Bsr.asin == 'cde')
        results = query.fetch()
        self.assertEqual(1, len(results))
        self.assertEqual(1, results[0].bsr)
        self.assertTrue(results[0].date < datetime.datetime.now())
    
    
    def testGetBsrs(self):
        dal = XSellDataAccessLayer()
        
        day_1_batch = [('abc', 1234), ('cde', 1)]
        before_1 = datetime.datetime.utcnow()

        dal.storeBsrs(day_1_batch)
        
        between_1_and_2 = datetime.datetime.utcnow()
      
        day_2_batch = [('abc', 5000), ('cde', 2)]        
        dal.storeBsrs(day_2_batch)
        
        after_2_batch = datetime.datetime.utcnow()

        list_asin_bsrs = dal.getBsrRanks(['abc'], between_1_and_2, after_2_batch)
        self.assertEqual(1, len(list_asin_bsrs))
        self.assertEqual('abc', list_asin_bsrs[0].asin)
        self.assertEqual(5000, list_asin_bsrs[0].bsr)
        
        list_asin_bsrs = dal.getBsrRanks(['abc', 'cde'], before_1, between_1_and_2)
        self.assertEqual(2, len(list_asin_bsrs))
        self.assertEqual('cde', list_asin_bsrs[0].asin)
        self.assertEqual(1, list_asin_bsrs[0].bsr)
        
        self.assertEqual('abc', list_asin_bsrs[1].asin)
        self.assertEqual(1234, list_asin_bsrs[1].bsr)
    
    def testStoreKeyword(self):
        dal = XSellDataAccessLayer()
        before_1 = datetime.datetime.utcnow()
        dal.storeKeywordRank("ABC", [(index, asin) for asin, index in enumerate(['a', 'b', 'c'])])
        
        dal.storeKeywordRank("ABC", [(index, asin) for asin, index in enumerate(['c', 'b', 'a'])])
        after_2 = datetime.datetime.utcnow()
        
        list_keywords = dal.getKeywordRanks(['a'], ['ABC'], before_1, after_2)
        self.assertEqual(0, list_keywords[0].order)
        self.assertEqual('a', list_keywords[0].asin)
        
        self.assertEqual(2, list_keywords[1].order)
        self.assertEqual('a', list_keywords[1].asin)
        
        
        
    def testGetKeywordRanks(self):
        dal = XSellDataAccessLayer()
        dal.storeKeywordRank("ABC", [(index, asin) for asin, index in enumerate(['a', 'b', 'c'])])
        dal.storeKeywordRank("ABC", [(index, asin) for asin, index in enumerate(['c', 'b', 'a'])])
        
        query = KeywordRank.query().filter(KeywordRank.keyword == 'ABC')
        results = query.fetch()
        self.assertEqual(6, len(results))
        self.assertTrue(results[0].date < datetime.datetime.now())
        
        query = KeywordRank.query().filter(KeywordRank.asin == 'a')
        results = query.fetch()
        self.assertEqual(2, len(results))
        self.assertEqual(0, results[0].order)
        self.assertEqual(2, results[1].order)        
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()