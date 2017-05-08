import webapp2
import logging

from amazon.api import AmazonAPI
from google.appengine.api import urlfetch
from google.appengine.ext import deferred

import os
import jinja2
from amzmri.dal.amazonDataAccessLayer import AmazonDataAccessLayer 
from amazon.credentials import *
from amzmri.services.listRankService import ListRankService
from amzmri.dal.xsellDataAccessLayer import XSellDataAccessLayer
from amzmri.services.product_fields_handler import ProductFieldsHandler
from amzmri.request_handlers.rank_report_request_handler import RankReportRequestHandler
from amzmri.request_handlers.reports_handler import ReportsHandler
from amzmri.request_handlers.asin_summary_handler import AsinSummaryHandler
from asklogin import LoginPage


competition = ['B0145QF41E', 'B00B7XUVOE', 'B0113GS1VY', 'B00AQ693RO', 'B011BY7DX0', 'B006P05S0Q', 'B01C03PLQW', 'B01DXIE29A',
               'B008436BJ4', 'B019VL5BB6', 'B00YXY3KHE', 'B00QC2AQ5Y', 'B01FIFPVXM', 'B01EQTJFHO']

PRODUCTS_PER_SEARCH_RESULT_PAGE = 17

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

_amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
_rankService = None
# product = amazon.lookup(ItemId='B0145QF41E')

class MainHandler(webapp2.RequestHandler):
    amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
    product = amazon.lookup(ItemId='B0145QF41E')
    
    def get(self):
        logging.info('MainHandler')
        template_values = {} 
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class GetProduct(webapp2.RequestHandler):

        
    def get(self):
        asin = self.request.get('asin', None)
        if not asin:
            self.response.write('please insert ASIN number')
            return
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
        try:
            product = amazon.lookup(ItemId=asin)
        except Exception as e:
            self.response.write('Exception has raised: ' + str(e))
        
        PRODUCT_ATTRIBUTES = [
            'asin', 'author', 'binding', 'brand', 'browse_nodes', 'ean', 'edition',
            'editorial_review', 'eisbn', 'features', 'get_parent', 'isbn', 'label',
            'large_image_url', 'list_price', 'manufacturer', 'medium_image_url',
            'model', 'mpn', 'offer_url', 'parent_asin', 'part_number',
            'price_and_currency', 'publication_date', 'publisher', 'region',
            'release_date', 'reviews', 'sku', 'small_image_url', 'tiny_image_url',
            'title', 'upc'
        ]
        
        logging.debug('all attr names: %s', product.__dict__.keys())
        for attribute in PRODUCT_ATTRIBUTES:
            attr_value = getattr(product, attribute)
            attr_value = attr_value.encode('utf-8') if attr_value and isinstance(attr_value, basestring) else attr_value
            if attribute == 'reviews' and len(attr_value) > 1 and attr_value[0]:
                result = urlfetch.fetch( url        = attr_value[1],  
                                         method     = urlfetch.GET,
                                         headers    = {'Content-Type': 'application/x-www-form-urlencoded'},
                                         deadline   = 60)
                if result and result.status_code == 200 and result.content:
                    self.response.write('<span style="color:red; font-size: 20px;">' + attribute + '</span>: ' + str(result.content) + '<br>')
                else:
                    self.response.write('<span style="color:red; font-size: 20px;">' + attribute + '</span>: cant retrieve reviews<br>')
            else:
                try:
                    self.response.write('<span style="color:red; font-size: 20px;">' + attribute + '</span>: ' + str(attr_value) + '<br>')
                except Exception as e:
                    logging.warning('exception raised: %s', e)
        
        
        # new images code
        logging.debug('product.images type: %s', str(type(product.images)))
        self.response.write('<span style="color:red; font-size: 20px;">image:</span>: <br>')
        image_counter = 1
        for image in product.images:
            imagUrl = image.LargeImage.URL
            logging.debug('image.LargeImage.URL: %s', image.LargeImage.URL)
            
            image_html = '<a download href="' + imagUrl + '">'
            image_html +=   '<img src="' + imagUrl + '"></img>'
            image_html += '</a>'
            image_html += '<br>'
            self.response.write(str(image_html))
            image_counter += 1

class GetProductsType(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(GetProductsType, self).__init__(request, response)
        self.amzDal = AmazonDataAccessLayer()
        
        if _amazon:
            logging.debug('from instance memory')
            self.amazon = _amazon
        else:
            logging.debug('NOT from instance memory')
            self.amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
        
    def get(self):
        return self.post();
    def post(self):
        asins = self.request.get('asin', None)
        field_type = self.request.get('field_type', None)
        
        html = u''
        if not asins or not field_type:
            return
        
        logging.debug('asin: %s | field_type: %s', asins, field_type)
        
        asins_list = asins.split(',')
        if field_type == 'reviews':
            self.response.write(self.getAllReviewsHtml(self.amazon, asins_list))
            return
        
        
        
        for asin in asins_list:
            asin = asin.strip()
            if not asin:
                continue
            try:
                self.product = self.amazon.lookup(ItemId=asin)
            except Exception as e:
                # TODO: create retry mechanism
                self.response.write('Exception has raised: ' + str(e) + ' on ASIN <b>' + str(asin) + '</b><br>')
                
            html += '<h4 style="clear: both;"><span style="color:red">' + field_type.upper() + '</span> | ' + asin + ' | <span style="color:blue">'
            try:
                html += self.product.title
            except Exception as e:
                logging.warning('exception raised: %s | on %s', e, self.product.title)
            html += '</span></h4>'
                
            if field_type == 'title':
                pass
            elif field_type == 'images':
                html += self.getAllImagesHtml(asin)
            elif field_type == 'features':
                html += self.getAllFeaturesHtml(asin)
            
                    

        self.response.write(html)
    
    def getAllReviewsHtmlOld(self, amazon, asins):
        products = amazon.lookup(ItemId=asins)
        
        lreviews = self.amzDal.getReviews(products)
        review_html = "<ul>"
        for review in lreviews:
            review_html += '<li>' + review + '</li>'
        review_html += '</ul><br>'
        return review_html
    
    def getAllReviewsHtml(self, amazon, asins):
        
        lStarToReviews = self.amzDal.getReviewsByStar(asins)
        review_html = ""
        for stars, lasinToReviewsTuples in lStarToReviews:
            review_html += "<h3>{0} stars</h3>".format(stars)
            for asin, lreviews in lasinToReviewsTuples:
                review_html += "<h4>{0}</h4>".format(asin)
                review_html += "<ul>"            
                for review in lreviews:
                    review_html += '<li>' + review + '</li>'
                review_html += '</ul>'
        return review_html
    
    def getAllFeaturesHtml(self, asin):
        features_html = '<ul>'
        logging.debug('self.product.features: %s', self.product.features)
        for feature in self.product.features:
            features_html += '<li>' + feature + '</li>'
        features_html += '</ul><br>'
        return features_html
    
    def getAllImagesHtml(self, asin):
        image_html = ''
        image_counter = 1
        image_prefix = asin
        image_html += '<ul style="float: left;">'
        for image in self.product.images:
            imagUrl = image.LargeImage.URL
            image_html += '<li class="baziliq_img_grid">'
            image_html += '<div class="baziliq_img_wrapper">'
            image_html +=   '<a download="' + str(image_prefix) + '_' + str(image_counter) + '" href="' + imagUrl + '">'
            image_html +=       '<img class="baziliq_img" src="' + imagUrl + '"></img>'
            image_html +=   '</a>'
            image_html += '</div>'
            image_html += '</li>'
            image_counter += 1
        image_html += '</ul>'
        image_html += '<br>'
        return image_html
        
        
class Search(webapp2.RequestHandler):
    def get(self):
        return self.post();
    def post(self):
        if _amazon:
            logging.debug('from instance memory')
            amazon = _amazon
        else:
            logging.debug('NOT from instance memory')
            amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
        
        search = 'Portable diaper changing pad'
        products = list(amazon.search_n(PRODUCTS_PER_SEARCH_RESULT_PAGE, ResponseGroup="Large", Keywords=search, SearchIndex='All'))
        self.response.write('got #'  + str(len(products)) + ' products for <b>"' + search + '"</b>: <br>' )
        for product in products:
            product_url = product.offer_url
            if product_url.endswith('/?tag=baziliq-20'):
                product_url = product_url[:-len('/?tag=baziliq-20')]
            self.response.write('* ' + product.asin + ' - ' + product.title + ' - <a href="' + product_url + '">' + product_url + '</a><br>')
#         self.response.write(products)


class SimilarProducts(webapp2.RequestHandler):
    def get(self):
        return self.post();
    def post(self):
        if _amazon:
            logging.debug('from instance memory')
            amazon = _amazon
        else:
            logging.debug('NOT from instance memory')
            amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
        similar_to_asin = 'B0145QF41E'
#         similar_to_asin = 'B00B7XUVOE,B0145QF41E'
        similar_products = amazon.similarity_lookup(ResponseGroup="Small", ItemId = similar_to_asin)
        self.response.write('got #'  + str(len(similar_products)) + ' similar products for <b>' + similar_to_asin + '</b>: <br>' )
        
        for product in similar_products:
            product_url = product.offer_url
            if product_url.endswith('/?tag=baziliq-20'):
                product_url = product_url[:-len('/?tag=baziliq-20')]
            self.response.write('* ' + product.asin + ' - ' + product.title + ' - <a href="' + product_url + '">' + product_url + '</a><br>')

class Crone(webapp2.RequestHandler):
    _rankService = None
    def get(self):
        return self.post();
    def post(self):
        if Crone._rankService is None:
            Crone._rankService = ListRankService(AmazonDataAccessLayer(), XSellDataAccessLayer())
        Crone._rankService.run()
        
        deferred.defer(scheduleUpdateProducts, _countdown = 5, _queue = "backendTask")

def scheduleUpdateProducts():
    logging.info('in scheduleUpdateProducts')
    update_products_fields_service = ProductFieldsHandler(AmazonDataAccessLayer(), XSellDataAccessLayer())
    update_products_fields_service.runUpdate()
    return
    
class UpdateProducts(webapp2.RequestHandler):
    def get(self):
        return self.post();
    def post(self):
        update_products_fields_service = ProductFieldsHandler(AmazonDataAccessLayer(), XSellDataAccessLayer())
        update_products_fields_service.runUpdate()
        
class GetProductChanges(webapp2.RequestHandler):
    def get(self):
        return self.post();
    def post(self):
        update_products_fields_service = ProductFieldsHandler(AmazonDataAccessLayer(), XSellDataAccessLayer())
        change_history = update_products_fields_service.getProductChangeHistory()
        if change_history:
            for change in change_history:
                self.response.write('<b>' + str(change.asin) + '</b> - ' + str(change.change_history) + ' | date: ' + str(change.creation_date) + '<br><br>')
        else:
            self.response.write('not found')

config = {'jinja' : JINJA_ENVIRONMENT}

app = webapp2.WSGIApplication([
    ('/', LoginPage),
    ('/product', GetProduct),
    ('/get_type_for_asin', GetProductsType),
    ('/search', Search),
    ('/get_similar_products', SimilarProducts),
    ('/rank_crone', Crone),
    ('/update_products', UpdateProducts),
    ('/reports', ReportsHandler),
    ('/asin_summary', AsinSummaryHandler),#AsinSummaryHandler
    ('/get_rank_report', RankReportRequestHandler),  
    ('/get_products_changes', GetProductChanges),
], debug=True, config=config)