'''
Created on 24 Aug 2016

@author: sergeykucher
'''

class AsinSummaryService(object):
    '''
    classdocs
    '''


    def __init__(self, xcell_data_access_layer):
        self._xcell_data_access_layer = xcell_data_access_layer
        
    
    def _fillBsrChange(self, list_bsr_ranks, dict_asin_to_report):
        '''
        Fill bsr reports with rank data
        '''
        
        for bsr_in_time in list_bsr_ranks:
            report = dict_asin_to_report[bsr_in_time.asin]
            report.ranks_in_time.append((bsr_in_time.bsr, bsr_in_time.date))
    
    
    def _fillKeyWordAverageChange(self, list_keyword_ranks, dict_asin_to_report):
        
        for keyword_rank in list_keyword_ranks:
            kw_report = dict_asin_to_report[keyword_rank.asin].keyword_reports[keyword_rank.keyword]
            kw_report.ranks_in_time.append((keyword_rank.order, keyword_rank.date))
    
    
    def summaryChangeReport(self, from_date, to_date, list_asins, list_keywords):
        dict_asin_to_report = {asin: AsinSummaryReport(list_keywords) for asin in list_asins}
                
        list_bsr_ranks = self._xcell_data_access_layer.getBsrRanks(list_asins, from_date, to_date)

        self._fillBsrChange(list_bsr_ranks, dict_asin_to_report)
        
        list_keyword_ranks = self._xcell_data_access_layer.getKeywordRanks(list_asins, list_keywords, from_date, to_date)
        
        self._fillKeyWordAverageChange(list_keyword_ranks, dict_asin_to_report)
        
        for report in dict_asin_to_report.itervalues():
            report.prepareReport()
        
        return dict_asin_to_report
    
    
class RankSummaryReport(object):
    def __init__(self):
        self.rank = None
        self.ranks_in_time = []
        self.rank_delta_percent = 0
    
    def prepareReport(self):
        sorted_rank_times = sorted(self.ranks_in_time, key=lambda rank_time : rank_time[1])
        self.ranks_in_time = None
        sorted_ranks = [rank_time[0] for rank_time in sorted_rank_times]        
        if len(sorted_ranks) == 0:return
        self.rank = sorted_ranks[-1] #last bsr is the relevant one
        prev_rank = sorted_ranks[0] #first is the one we want
        if prev_rank == 0: return
        self.rank_delta_percent =  ((self.rank - prev_rank)*1.0) / prev_rank
        
     
class AsinSummaryReport(RankSummaryReport):
    def __init__(self, list_keywords):
        RankSummaryReport.__init__(self)
        self.asin = None
        self.amazon_link = None
        self.small_picture = None
        self.keyword_reports = {keyword:KeywordSummaryReport(keyword) for keyword in list_keywords}
       
    def prepareReport(self):
        RankSummaryReport.prepareReport(self)
        kw_rank_sum = 0
        kw_delta_sum = 0
        num_keywods = 0
        for keyword_report in self.keyword_reports.itervalues():
            keyword_report.prepareReport()
            if keyword_report.rank is None: continue
            kw_rank_sum += keyword_report.rank
            kw_delta_sum += keyword_report.rank_delta_percent
            num_keywods += 1
        self.keyword_reports = None
        if num_keywods == 0: return
        
        self.kw_rank_average = kw_rank_sum * 1.0 / num_keywods
        self.kw_rank_average_delta_percent = kw_delta_sum* 1.0 / num_keywods
        
class KeywordSummaryReport(RankSummaryReport):
    def __init__(self, keyword):
        RankSummaryReport.__init__(self)
        self.keyword = keyword
        
        