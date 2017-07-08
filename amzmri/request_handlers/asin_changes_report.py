'''
Created on 16 Aug 2016

@author: sergeykucher
'''
import webapp2
import json
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
import datetime

class AsinChangesReport(webapp2.RequestHandler):
    _dal = None
    
    def _get_dal(self):
        if AsinChangesReport._dal is None:
            AsinChangesReport._dal = XSellDataAccessLayer()
        return AsinChangesReport._dal
        
    def get(self):
        return self.post()
    
    def post(self):
        xsell_dal = self._get_dal()
        to_date = datetime.datetime.utcnow()
        from_date = to_date - datetime.timedelta(days=7)
        d_asins = {}    
        for asin in xsell_dal.lAsins:
            d_asins[asin] = []
            product_changes = xsell_dal.getProductChangeHistory(asin, from_date, to_date)
            for product_change in product_changes:
                time = product_change.creation_date
                for property_name, (change_from, change_to) in product_change.change_history.iteritems():
                    d_asins[asin].append({
                                        'type': property_name,
                                        'from': change_from,
                                        'to':change_to,
                                        'time':time.strftime("%Y-%m-%d")
                                         })

        as_json = json.dumps(d_asins)
        self.response.write(as_json)
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "Content-Type"             
        

