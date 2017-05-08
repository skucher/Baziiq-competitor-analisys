
from amzmri.dal.tables.product_listing import ProductListing
import lxml

class ProductsDiffer(object):
    def __init__(self, from_product, to_product, amazon_api_access_layer, db_access_layer):
        self.amazon_api_access_layer = amazon_api_access_layer
        self.db_access_layer = db_access_layer
        self.from_product = from_product    # ProductListing
        self.to_product = to_product        # AmazonProduct

    def _get_by_index(self, lst, index):
        try:
            return lst[index]
        except IndexError:
            return ''
    
    def getDiffDict(self):
        diff_dict = {}
        property_names = ProductListing.getAllProductPropertyNames()
        for property_name in property_names:
            '''loop over ['asin', 'sku', 'features', 'title', 'mpn', 'brand', 'author', 'binding', 
                          'upc', 'image_urls', 'label', 'reviews', 'currency', 'last_modified', 'url', 
                          'description', 'price', 'manufacturer']
            '''
            changed_property_from, changed_property_to = self.getPropertyDiff(property_name)
            if changed_property_from or changed_property_to:
                diff_dict[property_name] = changed_property_from, changed_property_to
        
        return diff_dict
            
    def getPropertyDiff(self, property_name):
        ''' return tuple, the first element is the change from, and the second element is the change to  
        '''
        if property_name == 'asin':     # asin can't be chnaged
            return None, None
        elif property_name == 'title':
            if self.from_product.title != self.to_product.title:
                return self.from_product.title, self.to_product.title
        elif property_name == 'author':
            if self.from_product.author != self.to_product.author:
                return self.from_product.author, self.to_product.author 
        elif property_name == 'brand':
            if self.from_product.brand != self.to_product.brand:
                return self.from_product.brand, self.to_product.brand 
        elif property_name == 'binding':
            if self.from_product.binding != self.to_product.binding:
                return self.from_product.binding, self.to_product.binding 
        elif property_name == 'label':
            if self.from_product.label != self.to_product.label:
                return self.from_product.label, self.to_product.label 
        elif property_name == 'price':
            price, currency = self.to_product.price_and_currency
            if self.from_product.price != price:
                return self.from_product.price, price 
        elif property_name == 'manufacturer':
            if self.from_product.manufacturer != self.to_product.manufacturer:
                return self.from_product.manufacturer, self.to_product.manufacturer
        elif property_name == 'url':
            if self.from_product.url != self.amazon_api_access_layer.getProductUrl(self.to_product):
                return self.from_product.url, self.amazon_api_access_layer.getProductUrl(self.to_product)
        
        elif property_name == 'features':
            from_to = {'from': [],
                       'to': []}
            max_features = max(len(self.from_product.features),len(self.to_product.features))
            for feature_index in xrange(max_features):
                from_feature = self._get_by_index(self.from_product.features, feature_index)
                to_feature = self._get_by_index(self.to_product.features, feature_index)
                                
                if from_feature != to_feature:
                    from_to['from'].append(from_feature)
                    from_to['to'].append(to_feature)                                    
                    
            if from_to['from'] or from_to['to']:
                return from_to['from'], from_to['to']
        
        elif property_name == 'image_urls':
            if set(self.from_product.image_urls) != set([lxml.etree.tostring(image.LargeImage.URL) for image in self.to_product.images]):
                return self.from_product.image_urls, [lxml.etree.tostring(image.LargeImage.URL) for image in self.to_product.images]
        
        elif property_name == 'reviews':
            from_to = {'from': [],
                       'to': []}
            for star in xrange(1,6):
                current_product_reviews = self.amazon_api_access_layer.getReviews(self.to_product, star)
                if star in self.from_product.reviews and star in current_product_reviews and self.from_product.reviews[star] and current_product_reviews[star]:
                    set_from_product = set(self.from_product.reviews[star])
                    set_to_product = set(current_product_reviews[star])
                    diff_from_to = set_from_product - set_to_product
                    diff_to_from = set_to_product - set_from_product
                    if diff_from_to or diff_to_from:
                        from_to['from'][star] = diff_from_to
                        from_to['to'][star] = diff_to_from
                        
            if from_to['from'] or from_to['to']:
                return from_to['from'], from_to['to']
            
        elif property_name in ['sku', 'mnp', 'upc']:    # not likely change
            pass
        
        return None, None
        
