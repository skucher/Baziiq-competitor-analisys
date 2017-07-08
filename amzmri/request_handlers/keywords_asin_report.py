'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import webapp2
import json
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
import datetime

class KeywordsAsinReport(webapp2.RequestHandler):
    _dal = None
    
    def _get_dal(self):
        if KeywordsAsinReport._dal is None:
            KeywordsAsinReport._dal = XSellDataAccessLayer()
        return KeywordsAsinReport._dal
        
    def get(self):
        return self.post();


    def _format(self, asin_word_is_indexed):
        return [{'asin':e.asin,
                 'is_indexed' : e.words_is_indexed,
                 'time':e.date.strftime("%Y-%m-%d")} 
                for e in asin_word_is_indexed]
    
    def post(self):
        dal = self._get_dal()
        now = datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)        
        asin_word_is_indexed = dal.getOurAsinIndexes(week_ago, now)
        dict_res = self._format(asin_word_is_indexed)
        as_json = json.dumps(dict_res)
        self.response.write(as_json)
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "Content-Type"        
        

