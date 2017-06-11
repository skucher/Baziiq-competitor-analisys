'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import webapp2
import json
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer

class KeywordsAsinReport(webapp2.RequestHandler):
    _dal = None
    
    def _get_dal(self):
        if KeywordsAsinReport._dal is None:
            KeywordsAsinReport._dal = XSellDataAccessLayer()
        return KeywordsAsinReport._dal
        
    def get(self):
        return self.post();


    def _format(self, keywords_superset, asin_2_words_index):
        columns = ['ASIN']
        columns.extend(keywords_superset)
        rows = []
        for asin, d_words in asin_2_words_index.iteritems():
            row = [asin]
            row.extend(['1' if d_words[word] else '0' for word in keywords_superset])
            rows.append(row)
        return {'rows':rows,'columns':columns}
    
    def post(self):
        dal = self._get_dal()
        asin_2_words_index = dal.getOurAsinIndexes()
        dict_res = self._format(dal.keywords_superset, asin_2_words_index)
        #dict_res = {'asin':'ABC', 'data':{'rows':[['a','yes'],['b','no']],'columns':['keyword','is indexed']}}
        as_json = json.dumps(dict_res)
        self.response.write(as_json)
        

