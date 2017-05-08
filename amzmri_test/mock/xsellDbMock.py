'''
Created on 9 Aug 2016

@author: sergeykucher
'''

class XSellDbMock(object):
    def __init__(self):
        self.keywords = []
        self.dBsrs = {}
        self.dKeywordToAsins = {}
        self.lAsins = []
    
    def storeBsrs(self, lAsinBsr):
        for asin, bsr in lAsinBsr:
            self.dBsrs[asin] = bsr

    def storeKeywordRank(self, keyword, lAsinToRankTuple):
        self.dKeywordToAsins[keyword] = lAsinToRankTuple
    
    def getKeywords(self):
        return self.keywords
    
    def getProductSearchLimit(self):
        return 25
    
    def getAsins(self):
        return self.lAsins
    
    '''
    for amzProduct in self.amzProducts:
            self.mriDal.storeBsrs(amzProduct.asin, amzProduct.bsr)            
        keywords = self.mriDal.getKeywords()
        
        prodSearchLimit = self.mriDal.getProductSearchLimit()
        for keyword in keywords:
            dAsinToRank = self.amzDal.searchNAsins(keyword, prodSearchLimit)
            self.mriDal.storeKeywordRank(keyword, dAsinToRank)
    '''
        
        