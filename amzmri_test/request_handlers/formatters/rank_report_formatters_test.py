'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import unittest
from datetime import datetime
from amzmri.request_handlers.fomatters.rank_report_formatters import RankTableFormatter,\
    RankTableChartFormatter
from amzmri.services.rank_report_service import AsinReport


class RankTableFormatterTest(unittest.TestCase):


    def testFormat(self):
        ar1 = AsinReport()
        ar1.list_bsr_ranks = [('1', datetime.now()),('2', datetime.now()),('3', datetime.now())]
        ar1.dict_keyword_ranks = {'kw1':[('1', datetime.now()),('2', datetime.now()),('3', datetime.now())] }

        ar2 = AsinReport()
        ar2.list_bsr_ranks = [('11', datetime.now()),('21', datetime.now()),('31', datetime.now())]
        ar2.dict_keyword_ranks = {'kw1':[('11', datetime.now()),('21', datetime.now()),('31', datetime.now())] }
                
        asin_bsrs = [('asin1',ar1), ('asin2',ar2)]
        
        formatter = RankTableFormatter()
        as_json = formatter.format(asin_bsrs, ['kw1'])
        
        self.assertEqual('{"rows": [["asin1", "1 -> 2 -> 3", "1 -> 2 -> 3"], ["asin2", "11 -> 21 -> 31", "11 -> 21 -> 31"]], "columns": ["Asin", "Bsr", "kw1"]}', as_json)
        
        
class RankTableChartFormatterTest(unittest.TestCase):


    def testFormat(self):
        ar1 = AsinReport()
        ar1.list_bsr_ranks = [('1', datetime.now()),('2', datetime.now()),('3', datetime.now())]
        ar1.dict_keyword_ranks = {'kw1':[('1', datetime.now()),('2', datetime.now()),('3', datetime.now())] }

        ar2 = AsinReport()
        ar2.list_bsr_ranks = [('11', datetime.now()),('21', datetime.now()),('31', datetime.now())]
        ar2.dict_keyword_ranks = {'kw1':[('11', datetime.now()),('21', datetime.now()),('31', datetime.now())] }
                
        asin_bsrs = [('asin1',ar1), ('asin2',ar2)]
        
        formatter = RankTableChartFormatter()
        as_json = formatter.format(asin_bsrs, ['kw1'])
        
        self.assertEqual('{"asins_data": '+
                             '[{"bsrs": [[17, "1"], [17, "2"], [17, "3"]], "asin": "asin1", "keyword_rows": [[17, "3"]]}, '+
                              '{"bsrs": [[17, "11"], [17, "21"], [17, "31"]], "asin": "asin2", "keyword_rows": [[17, "31"]]}], '+
                           '"rows": [["asin1", "<div id=\\"baziliq_result_bsr_asin1\\"></div>", "<div id=\\"baziliq_result_keywords_asin1\\"></div>"], '+
                                   '["asin2", "<div id=\\"baziliq_result_bsr_asin2\\"></div>", "<div id=\\"baziliq_result_keywords_asin2\\"></div>"]], '+
                           '"columns": ["Asin", "Bsr", "Keywords"], '+
                           '"keyword_names": ["kw1"]}', as_json)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFormat']
    unittest.main()