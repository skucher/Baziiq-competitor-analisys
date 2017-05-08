'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import webapp2
from amzmri.services.rank_report_service import RankReportService
import datetime
from amzmri.request_handlers.fomatters.rank_report_formatters import RankFormatterFactory,\
    RankTableFormatter
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer


class RankReportRequestHandler(webapp2.RequestHandler):
    _service = None
    
    def _getService(self):
        if RankReportRequestHandler._service is not None:
            return RankReportRequestHandler._service        
        xsell_dal = XSellDataAccessLayer()
        
        return RankReportService(xsell_dal)

    def _getFormatter(self):
        return RankTableFormatter()
        '''
        report_type = self.request.get('report_type', None)
        if report_type is None:
            return None
        formatter = RankFormatterFactory.create(report_type)
        return formatter
        '''
                
    def get(self):
        return self.post();

    def post(self):
        formatter = self._getFormatter()
        if(formatter is None):
            raise ImportError("Formatter doesnt exist")
        
        service = self._getService()
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)
        list_asins = service._xcell_data_access_layer.getAsins()
        list_keywords = service._xcell_data_access_layer.getKeywords()
        
        list_asin_reports = service.reportRank(week_ago, now, list_asins, list_keywords)
        as_json = formatter.format(list_asin_reports, list_keywords)
        self.response.write(as_json)
        

