'''
Created on 24 Aug 2016

@author: sergeykucher
'''
import unittest
from amzmri.services.asin_summary_service import RankSummaryReport,\
    AsinSummaryReport, KeywordSummaryReport, AsinSummaryService
from amzmri_test.mock.amzDalMock import AmzDalMock
from amzmri.dal.tables.keywordRank import KeywordRank
from amzmri.dal.tables.bsr import Bsr


class AsinSummaryServiceTest(unittest.TestCase):


    def testRankSummaryReport(self):
        report = RankSummaryReport()
        report.ranks_in_time = [(2, 1), (3, 3),  (2, 2)]
        report.prepareReport()
        self.assertEqual(3, report.rank)
        self.assertEqual(0.5, report.rank_delta_percent)

    def testAsinSummaryReport(self):
        report = AsinSummaryReport(['k1','k2'])
        report.ranks_in_time = [(2, 1), (3, 3),  (2, 2)]
        
        report.keyword_reports['k1'] = KeywordSummaryReport('k1')
        report.keyword_reports['k1'].ranks_in_time = [(2, 1), (3, 3)]
        report.keyword_reports['k2'] = KeywordSummaryReport('k2')
        report.keyword_reports['k2'].ranks_in_time = [(5, 1), (10, 3)]
        report.prepareReport()
        self.assertEqual(3, report.rank)
        self.assertEqual(0.5, report.rank_delta_percent)
        
        self.assertEqual(6.5, report.kw_rank_average)
        self.assertEqual(0.75, report.kw_rank_average_delta_percent)
                
    def testSummaryChangeReport(self):
        dal_mock = AmzDalMock()
        list_keywords = [KeywordRank(asin='1', order=1, keyword='k'), KeywordRank(asin='1', order=12, keyword='k')]
        dal_mock.getKeywordRanks = lambda a, b, c, d : list_keywords
        
        list_bsrs = [Bsr(asin='1', bsr=15), Bsr(asin='1', bsr=20)]
        dal_mock.getBsrRanks = lambda a, b, c : list_bsrs
        service = AsinSummaryService(dal_mock)
        dict_asin_to_report = service.summaryChangeReport(1, 2, ['1'], ['k'])
        report = dict_asin_to_report['1']
        self.assertEqual(20, report.rank)
        self.assertAlmostEqual(0.33333, report.rank_delta_percent, 3)
        
        self.assertEqual(12, report.kw_rank_average)
        self.assertEqual(11.0, report.kw_rank_average_delta_percent)
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()