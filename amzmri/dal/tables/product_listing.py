from google.appengine.ext import ndb

# https://cloud.google.com/appengine/docs/python/ndb/entity-property-reference
class ProductListing(ndb.Model):
    ''' Product full listing - like it shows in Amazon at present time - asin should have a unique value
    '''
    asin = ndb.StringProperty()
    
    title = ndb.StringProperty()
    author = ndb.StringProperty()
    brand = ndb.StringProperty()
    price = ndb.FloatProperty()
    currency = ndb.StringProperty()
    manufacturer = ndb.StringProperty()
    url = ndb.StringProperty()
    binding = ndb.StringProperty()
    description = ndb.TextProperty()    # editorial_review field
    label = ndb.StringProperty()
    
    sku = ndb.StringProperty()
    mpn = ndb.StringProperty()
    upc = ndb.StringProperty()          # maybe it should be an integer?
    
    features = ndb.StringProperty(repeated = True)    # TODO: maybe change to ndb.JsonProperty or PickleProperty or compressed blob
    image_urls = ndb.StringProperty(repeated = True)   # https://cloud.google.com/appengine/docs/python/ndb/queries#repeated_properties
    reviews = ndb.JsonProperty(compressed = True)
    
    last_modified = ndb.DateTimeProperty(auto_now = True)
    
    @classmethod
    def getAllProductPropertyNames(self):
        return set(dir(ProductListing())) - set(dir(ndb.Model()))

        
        
        