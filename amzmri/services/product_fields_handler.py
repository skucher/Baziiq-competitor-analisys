
from amzmri.dal.tables.product_listing import ProductListing
from google.appengine.ext import ndb
from amzmri.services.product_change_calc import ProductsDiffer
import logging
import lxml
from amzmri.dal.tables.product_change_history import ProductChangeHistory
import datetime

class ProductFieldsHandler(object):
    def __init__(self, amazon_api_access_layer, db_access_layer):
        self.amazon_api_access_layer = amazon_api_access_layer
        self.db_access_layer = db_access_layer
        
    def runUpdate(self):
        asin_list = self.db_access_layer.getAsins()
        products = self.amazon_api_access_layer.getProductsByAsins(asin_list)

        logging.debug('found #%d products for the ASINs: %s', len(products), asin_list)
        
        for product in products:          
            cur_asin = product.asin
            logging.debug('looping over ASIN %s', cur_asin)
            product_key = ndb.Key('ProductListing', cur_asin)
            db_product = product_key.get()
            
            if db_product:
                product_differ = ProductsDiffer(db_product, product, self.amazon_api_access_layer, self.db_access_layer)
                changed_properties_dict = product_differ.getDiffDict()
                if changed_properties_dict:  
                    logging.debug('change detected')
                    self.db_access_layer.updateProductByProperties(db_product, product, self.amazon_api_access_layer, changed_properties_dict.keys())
                    self.updateProductChangeHistory(cur_asin, changed_properties_dict)
                else:
                    logging.debug('NO change detected')
            else:   # product not exists
                logging.debug('product not exists - creating new one :-)')
                price, currency = product.price_and_currency
                new_product = ProductListing(key = product_key,
                                             asin = cur_asin,
                                             title = product.title,
                                             author = product.author,
                                             brand = product.brand,
                                             price = price,
                                             currency = currency,
                                             manufacturer = product.manufacturer,
                                             url = self.amazon_api_access_layer.getProductUrl(product),
                                             binding = product.binding,
                                             description = product.editorial_review,
                                             label = product.label,
                                             sku = product.sku,
                                             mpn = product.mpn,
                                             upc = product.upc,
                                             features = product.features,
                                             image_urls = [lxml.etree.tostring(image.LargeImage.URL) for image in product.images],
                                             reviews = {star: self.amazon_api_access_layer.getReviews(product, star) \
                                                        for star in xrange(1,6)}                                            
                )
                new_product.put()
            
                
    def updateProductChangeHistory(self, asin, changed_properties_dict):
        # temporary code, to make sure that there are no more than 2 entities that are created in the same day
        current_time = datetime.datetime.now()
        query = ProductChangeHistory.query(
            ndb.AND(ProductChangeHistory.creation_date >= current_time.replace(hour=0, minute=0, second=0, microsecond=0)),
                    ProductChangeHistory.creation_date < current_time.replace(hour=23, minute=59, second=59, microsecond=0),
                    ProductChangeHistory.asin == asin)                       
        product_change_history = query.get()
        if product_change_history:      # already have a chage history log for today - lets update him instead of creating a new one
            new_change_history = product_change_history.change_history
            for property_name, (from_change, to_change) in changed_properties_dict.iteritems():
                if property_name in new_change_history:
                    new_change_history[property_name] = (new_change_history[property_name][0], to_change)
            if new_change_history != product_change_history.change_history:     # if we found a change then update the DB
                product_change_history.change_history = new_change_history
                product_change_history.put()
            logging.info('saving UPDATE ProductChangeHistory for asin %s | %s', asin, new_change_history)
        else:
            logging.info('saving NEW ProductChangeHistory for asin %s | %s', asin, changed_properties_dict)
            product_change = ProductChangeHistory(asin = asin,
                                                  change_history = changed_properties_dict)
            product_change.put()
            
    def getProductChangeHistory(self, asins = None, from_date = datetime.datetime.now() - datetime.timedelta(days=7), to_date = datetime.datetime.now()):
        # check how to combine and queries with regular
        query = ProductChangeHistory.query(
            ndb.AND(ProductChangeHistory.creation_date >= from_date.replace(hour=0, minute=0, second=0, microsecond=0),
                    ProductChangeHistory.creation_date < to_date.replace(hour=23, minute=59, second=59, microsecond=0)))
        if asins:
            query = query.query(ProductChangeHistory.asin.IN(asins))
        query = query.order(-ProductChangeHistory.creation_date)
        product_change_histories = query.fetch(100)
        return product_change_histories
            
        
        
        
    