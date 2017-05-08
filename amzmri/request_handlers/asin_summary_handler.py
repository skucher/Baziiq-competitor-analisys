'''
Created on 24 Aug 2016

@author: sergeykucher
'''
import webapp2
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
from amzmri.services.asin_summary_service import AsinSummaryService
import json
import datetime

class AsinSummaryHandler(webapp2.RequestHandler):
    _service = None
    
    def _getService(self):
        if AsinSummaryHandler._service is not None:
            return AsinSummaryHandler._service        
        xsell_dal = XSellDataAccessLayer()        
        return AsinSummaryService(xsell_dal)

    def get(self):
        return self.post();
 
    def post(self):
       
        service = self._getService()
        list_asins = service._xcell_data_access_layer.getAsins()
        list_keywords = service._xcell_data_access_layer.getKeywords()
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)
        list_asin_summary_reports = service.summaryChangeReport(week_ago, now, list_asins, list_keywords)
        as_json = json.dumps(list_asin_summary_reports, default=lambda o: o.__dict__, 
            sort_keys=True)
        self.response.write(as_json)
        
        
        