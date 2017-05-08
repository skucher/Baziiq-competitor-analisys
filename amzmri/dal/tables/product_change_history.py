
from google.appengine.ext import ndb

class ProductChangeHistory(ndb.Model):
    asin = ndb.StringProperty(required = True)
    change_history = ndb.JsonProperty(compressed = True)
    creation_date = ndb.DateTimeProperty(auto_now_add = True)
    