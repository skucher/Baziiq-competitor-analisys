'''
Created on 11 Jun 2017

@author: sergeykucher
'''

from google.appengine.ext import ndb

class AsinWordsIsIndexed(ndb.Model):
    asin = ndb.StringProperty(required = True)
    words_is_indexed = ndb.StringProperty(required = True)
    date = ndb.DateTimeProperty(auto_now=True)    
