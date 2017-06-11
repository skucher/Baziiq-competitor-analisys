import logging
import webapp2
from amzmri.services.list_rank_service import ListRankService
from amzmri.dal.amazonDataAccessLayer import AmazonDataAccessLayer
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
from amzmri.services.product_fields_handler import ProductFieldsHandler
from google.appengine.ext.deferred import deferred
from amzmri.services.kerwords_asin_service import KeywordsAsinService
class Crone(webapp2.RequestHandler):
    _rankService = None
    _keword_asin_service = None
        
    def get(self):
        return self.post();
    def post(self):
        amz_dal = AmazonDataAccessLayer()
        xsel_dal = XSellDataAccessLayer()
        if Crone._rankService is None:
            Crone._rankService = ListRankService(amz_dal, xsel_dal)
            
        Crone._rankService.run()
        if Crone._keword_asin_service is None:
            Crone._keword_asin_service = KeywordsAsinService(amz_dal, xsel_dal)
            
        Crone._keword_asin_service.run()
        
        deferred.defer(scheduleUpdateProducts, _countdown = 5, _queue = "backendTask")

def scheduleUpdateProducts():
    logging.info('in scheduleUpdateProducts')
    update_products_fields_service = ProductFieldsHandler(AmazonDataAccessLayer(), XSellDataAccessLayer())
    update_products_fields_service.runUpdate()
    return