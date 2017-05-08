'''
Created on 9 Aug 2016

@author: sergeykucher
'''
from google.appengine.ext import ndb

class Bsr(ndb.Model):
    asin = ndb.StringProperty(required = True)
    bsr = ndb.IntegerProperty(required = True)
    date = ndb.DateTimeProperty(auto_now=True)