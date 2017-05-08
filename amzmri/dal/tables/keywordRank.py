'''
Created on 9 Aug 2016

@author: sergeykucher
'''

from google.appengine.ext import ndb

class KeywordRank(ndb.Model):
    keyword = ndb.StringProperty(required = True)
    asin = ndb.StringProperty(required = True)
    order = ndb.IntegerProperty(required = True)
    date = ndb.DateTimeProperty(auto_now=True)
        