import unittest
from amzmri.services.listRankService import ListRankService
from amzmri_test.mock.xsellDbMock import XSellDbMock
from amzmri_test.mock.amzDalMock import AmzDalMock

class ListRankServiceTest(unittest.TestCase):
   

    def test_runEmptyDb(self):
        amzDal = AmzDalMock()
        xcellDal = XSellDbMock()
        service = ListRankService(amzDal, xcellDal)
        service.run()
        self.assertEqual(0, len(xcellDal.dBsrs), 'no bsrs')


    def test_runOneTwoAsinsKeywords(self):
        amzDal, xcellDal = self._prepForTwoAsins()
        service = ListRankService(amzDal, xcellDal)
        service.run()
        
        self.assertEqual(('abc', 1), xcellDal.dKeywordToAsins['hi'][0])
        self.assertEqual(('cde', 25), xcellDal.dKeywordToAsins['hi'][1])
        
        self.assertEqual(('abc', 3), xcellDal.dKeywordToAsins['bye'][0])
        self.assertEqual(('cde', 2), xcellDal.dKeywordToAsins['bye'][1])
        
        self.assertFalse('other' in xcellDal.dKeywordToAsins)
        
        
    def test_runOneTwoAsinsBsrs(self):
        amzDal, xcellDal = self._prepForTwoAsins()
        service = ListRankService(amzDal, xcellDal)
        service.run()
        
        self.assertEqual(('abc', 1), xcellDal.dKeywordToAsins['hi'][0])
        self.assertEqual(('cde', 25), xcellDal.dKeywordToAsins['hi'][1])
        
        self.assertEqual(('abc', 3), xcellDal.dKeywordToAsins['bye'][0])
        self.assertEqual(('cde', 2), xcellDal.dKeywordToAsins['bye'][1])
        
        self.assertFalse('other' in xcellDal.dKeywordToAsins)
    
    def _prepForTwoAsins(self):          
        amzDal = AmzDalMock()
        amzDal.lAsinRanks = [('abc', 13), ('cde', 1), ('not_relevant', 1)]      
        amzDal.dKeywordAsins = {
                                "hi":  {'abc': 1}, 
                                "bye": {'abc': 3 , 'cde': 2} ,
                                "other" : {'abc': 3 , 'cde': 2}  ,
                                }
        xcellDal = XSellDbMock()
        xcellDal.keywords = ['hi', 'bye']
        xcellDal.lAsins = ['abc','cde']
        return  amzDal, xcellDal
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()