'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import unittest
from amzmri.services.rank_report_service import RankReportService


class RankReportServiceTest(unittest.TestCase):
    
    def setUp(self):
        self._service = RankReportService()
        pass

    def testSimple(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()