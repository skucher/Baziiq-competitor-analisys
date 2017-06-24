import webapp2
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
import datetime
import json

class AsinHistoryHandler(webapp2.RequestHandler):
    def get(self):
        return self.post();
 
    '''
    {'B01ETRM2LO':{     
    'bsr':[{"value":80400,"time":1},{"value":27000,"time":13000}],
    "keywords": { 
        'kw1':[{"value":80400,"time":1},{"value":27000,"time":13000}]
        }
    "changes":{
        'type': 'title',
        'from': 'abc',
        'to':'cde'
        }    
    },...}
    '''

    
    def _create_d_asins(self,list_asin_bsrs):
        d_asins = {}
        for bsr_obj in list_asin_bsrs:
            d_asins[bsr_obj.asin] = {'bsr':[],'keywords':{},'changes':{}}
        return d_asins
    
    def post(self):       
        xsell_dal = XSellDataAccessLayer()
        list_asins = xsell_dal.getAsins()
        to_date = datetime.datetime.utcnow()
        from_date = to_date - datetime.timedelta(days=30)
        
        list_asin_bsrs = xsell_dal.getBsrRanks(list_asins, from_date, to_date)
        d_asins = self._create_d_asins(list_asin_bsrs)
        
        
        for bsr_obj in list_asin_bsrs:
            d_asins[bsr_obj.asin]['bsr'].append({"value":bsr_obj.bsr,"time":bsr_obj.date.strftime("%Y-%m-%d")})
        
        list_kewword_ranks = xsell_dal.getKeywordRanks(list_asins, xsell_dal.lKeywords, from_date, to_date)
        
        for keyword_rank_obj in list_kewword_ranks:
            current_dict_kws = d_asins[keyword_rank_obj.asin]['keywords']
            current_history = current_dict_kws.setdefault(keyword_rank_obj.keyword,[])
            current_history.append({"value":keyword_rank_obj.order,"time":keyword_rank_obj.date.strftime("%Y-%m-%d")})
        
        d_result = {
                    'asins': d_asins,
                    'keywords': xsell_dal.lKeywords,
                    }
        
        as_json = json.dumps(d_result)
        self.response.write(as_json)
          
        

