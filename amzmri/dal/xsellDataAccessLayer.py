
from google.appengine.ext import ndb
from amzmri.dal.tables.bsr import Bsr
from amzmri.dal.tables.keywordRank import KeywordRank
import lxml
import datetime
from amzmri.dal.tables.product_change_history import ProductChangeHistory
import logging

class XSellDataAccessLayer(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.lAsins = ['B01ETRM2LO', 'B0038JE3R6', 'B0145QF41E', 'B00B7XUVOE', 'B0113GS1VY', 'B01DXIE29A', 'B01C03PLQW', 'B00S3HGG9Q', 'B00AQ693RO', 'B011BY7DX0', 'B017139DQK']
        self.lKeywords = [
                            'nappy changing bag',
                            'diaper changing pad',
                            "diaper changing mat",
                            "diaper changing station",
                            "portable diaper changing pad",
                            'diaper changing kit',
                            'travel diaper changing pad',
                            'diaper changing clutch',
                            'travel diaper changing kit',
                            'portable changing mat',
                            'portable changing matt',
                            'portable changing pad',
                            'travel changing mat',
                            'travel changing pad',
                            'diaper change pad',
                            'diaper changer',
                            'diaper change mat',
                            'diaper change station',
                            'diaper change organizer',
                        ]    
           
    def storeBsrs(self, lAsinBsrs):
        '''
        lAsinBsrs is asin, bsr tupple
        '''
        models = []
        for asin, bsr in lAsinBsrs:
            bsrModel = Bsr(asin=asin, bsr=bsr)
            models.append(bsrModel)
        ndb.put_multi(models)
        
    def storeKeywordRank(self, keyword, lAsinsOrdered):
        models = []
        for asin, index in lAsinsOrdered:
            keywordRank = KeywordRank(asin=asin, order=index, keyword=keyword)
            models.append(keywordRank)       
        ndb.put_multi(models)    
    
    def getBsrRanks(self, list_asins, from_date, to_date):
        set_asins = set(list_asins)
        query = Bsr.query(
            ndb.AND(Bsr.date >= from_date),
                    Bsr.date < to_date,
                    Bsr.asin.IN(set_asins))
        bsr_entities = query.fetch()
        return bsr_entities
        
    def getKeywordRanks(self, list_asins, list_keywords, from_date, to_date):
        set_asins = set(list_asins)
        set_keywords = set(list_keywords)
        query = KeywordRank.query(
            ndb.AND(KeywordRank.date >= from_date),
                    KeywordRank.date < to_date,
                    KeywordRank.keyword.IN(set_keywords),
                    KeywordRank.asin.IN(set_asins))
        keyword_entities = query.fetch()
        return keyword_entities
        
    def getKeywords(self):
        return self.lKeywords
    
    def getProductSearchLimit(self):
        return 100
    
    def getAsins(self):
        return self.lAsins
    
    
    def updateProductByProperties(self, db_product, amazon_product, amazon_api_access_layer, property_names_to_update=None):
        ''' parameters: db_product - ProductListing
                        amazon_product - AmazonProduct
                        amazon_api_access_layer - AmazonDataAccessLayer
                        property_names_to_update - list of changed property names
                        
                        updating db_product with all the changes from amazon_product, and writing the up-to-date product back to the Datastore
        '''
        if not property_names_to_update:
            return
        
        need_to_update = False
        for property_name in property_names_to_update:
            if property_name == 'title' and db_product.title != amazon_product.title:
                db_product.title = amazon_product.title
                need_to_update = True
            elif property_name == 'author' and db_product.author != amazon_product.author:
                db_product.author = amazon_product.author
                need_to_update = True
            elif property_name == 'brand' and db_product.brand != amazon_product.brand:
                db_product.brand = amazon_product.brand
                need_to_update = True
            elif property_name == 'binding' and db_product.binding != amazon_product.binding:
                db_product.binding = amazon_product.binding
                need_to_update = True
            elif property_name == 'label' and db_product.label != amazon_product.label:
                db_product.label = amazon_product.label
                need_to_update = True
            elif property_name == 'price':
                new_price = self._try_extract_price(amazon_product)
                if new_price <> db_product.price:
                    db_product.price = new_price
                    need_to_update = True
            elif property_name == 'manufacturer' and db_product.manufacturer != amazon_product.manufacturer:
                db_product.manufacturer = amazon_product.manufacturer
                need_to_update = True
            elif property_name == 'url' and db_product.url != amazon_api_access_layer.getProductUrl(amazon_product):
                db_product.url = amazon_api_access_layer.getProductUrl(amazon_product)
                need_to_update = True
            elif property_name == 'features' and db_product.features != amazon_product.features:
                db_product.features = amazon_product.features
                need_to_update = True
            elif property_name == 'image_urls' and \
                    set(db_product.image_urls) != set([lxml.etree.tostring(image.LargeImage.URL) for image in amazon_product.images]):
                db_product.image_urls = [lxml.etree.tostring(image.LargeImage.URL) for image in amazon_product.images]
                need_to_update = True
            elif property_name == 'reviews':
                db_product.reviews = {star: amazon_api_access_layer.getReviews(amazon_product, star) \
                                                        for star in xrange(1, 6)}
                need_to_update = True
            
        if need_to_update:
            db_product.put()
    
    
    def getProductChangeHistory(self, asin, from_date=datetime.datetime.now(), to_date=datetime.datetime.now()):
        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)  # beginning of the day
        to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=0)  # end of the day
        query = ProductChangeHistory.query(
            ndb.AND(ProductChangeHistory.creation_date >= from_date),
                    ProductChangeHistory.creation_date < to_date,
                    ProductChangeHistory.asin == asin).get()
        product_change_history = query.fetch(100)
        
        if not product_change_history:
            logging.debug('ProductChangeHistory not found')
        else:
            logging.debug('found %d ProductChangeHistory', len(product_change_history))
        
        return product_change_history
    
    def _try_extract_price(self, amazon_product):
        try:
            return float(amazon_product.price_and_currency[0])
        except Exception, e:
            print 'ERROR: Product: %s price is not float: %s - error: %s' %(amazon_product.asin,str(amazon_product.price_and_currency),str(e))
            return -9999