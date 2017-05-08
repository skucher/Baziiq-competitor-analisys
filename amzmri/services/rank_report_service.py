'''
Created on 16 Aug 2016

@author: sergeykucher
'''

class RankReportService(object):

    def __init__(self, xcell_data_access_layer):
        '''
        Constructor
        '''
        self._xcell_data_access_layer = xcell_data_access_layer
    
    def reportRank(self, from_date, to_date, list_asins, list_keywords):
        '''
        returns: dictionary - {asin: AsinReport}
        '''
        list_bsr_ranks = self._xcell_data_access_layer.getBsrRanks(list_asins, from_date, to_date)

        dict_report = {} #asin to list of bst date tuples
        for bsr_rank in list_bsr_ranks:
            asin_report = dict_report.setdefault(bsr_rank.asin, AsinReport())
            asin_report.list_bsr_ranks.append((bsr_rank.bsr, bsr_rank.date))#convert date to day?
        
        list_keyword_ranks = self._xcell_data_access_layer.getKeywordRanks(list_asins, list_keywords, from_date, to_date)
        for keyword_rank in list_keyword_ranks:
            asin_report = dict_report.setdefault(keyword_rank.asin, AsinReport())
            keyword_results = asin_report.dict_keyword_ranks.setdefault(keyword_rank.keyword, [])
            keyword_results.append((keyword_rank.order, keyword_rank.date))#convert date to day?
        
        
        return dict_report.items()
    
class AsinReport(object):
    def __init__(self):
        self.list_bsr_ranks = []
        self.dict_keyword_ranks = {}
        
        