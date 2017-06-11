
from google.appengine.api import urlfetch
from bs4 import BeautifulSoup
from utils.listExt import ListExt
import logging
from amazon.credentials import *
from amzmri.dal.amz_api_extension import AmazonAPIExt

class AmazonDataAccessLayer(object):
    
    def __init__(self):
        self._amazonApi = AmazonAPIExt(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
    
    def getReviewsByStar(self, lAsins):
        products = self._getProducts(lAsins)        
        lStars = []
        for star in xrange(1,6):
            lReviews = []
            for product in products:
                prodReviews = self.getReviews(product, star)
                lReviews.append((product.asin, prodReviews))
            lStars.append((star, lReviews))
        return lStars
    
    def getReviews(self, product, star):
        '''
        returns list reviews        
        '''
        startsStr = self._converStars(star)
        soup = self._getProductReviewSoup(product, startsStr)
        reviewTags = soup.findAll('span',{'class' : lambda x: x and 'review-text' in x})
        reviews =[review.text.encode('utf8') for review in reviewTags]
        return reviews 
    
    
    def searchFirstNAsins(self, search, prodSearchLimit):
        products = self._amazonApi.search_n(prodSearchLimit, 
                                 ResponseGroup="ItemIds", 
                                 Keywords=search, 
                                 SearchIndex='Baby')
        
        return {p.asin: index for index, p in enumerate(products)}
     
    def getProductsByAsins(self, lAsins):
        return self._getProducts(lAsins, "Medium")

    def getRankForAsins(self, lAsins):
        products = self._getProducts(lAsins, "SalesRank")
        return [(p.asin, int(p.sales_rank)) for p in products]
    
    def getStockForAsins(self, lAsins):
        products = self._getProducts(lAsins, "OfferFull")
        print products
        
    def get_is_indexed_for_words(self, asin, set_words):
        d_res = {}
        for word in set_words:
            products = self._amazonApi.search_n(1, 
                                     ResponseGroup="ItemIds", 
                                     Keywords="%s %s" % (asin, word), 
                                     SearchIndex='Baby')
            d_res[word] = True if products else False 
        return d_res
    
    def getProductUrl(self, product):
        product_url = product.offer_url
        if product_url.endswith('/?tag=baziliq-20'):
            product_url = product_url[:-len('/?tag=baziliq-20')]
        return product_url
    #region Private
    
    
    def _getProductReviewSoup(self, product, startsStr):
        url = '''http://www.amazon.com/product-reviews/%s/?filterByStar=%s''' % (product.asin, startsStr)
        try:
            f = urlfetch.fetch(url)
            page = f.content;
        except Exception, e:
            logging.error("Unable to get review for: %s" % e)
            page = ""
        soup = BeautifulSoup(page, 'html.parser')
        return soup     
                 
    def _converStars(self, numStars):
        if numStars == 1:
            return "one_star"
        if numStars == 2:
            return "two_star"
        if numStars == 3:
            return "three_star"
        if numStars == 4:
            return "four_star"
        if numStars == 5:
            return "five_star"
        raise NotImplemented()    
    
    def _getProducts(self, lAsins, responseGroup = None):
        products = []
        chunks = ListExt.chunks(lAsins, 10)
        for chunk in chunks:
            sChunk = ",".join(chunk)
            currProducts = self._amazonApi.lookup(ItemId=sChunk, ResponseGroup=responseGroup)
            if isinstance(currProducts, list):
                products.extend(currProducts)
            else:
                products.append(currProducts)
        return products
    
    #endregion