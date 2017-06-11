'''
Created on 9 Aug 2016

@author: sergeykucher
'''
import time
class ListRankService(object):
    
    def __init__(self, amzDal, xsellDal):
        self.xsellDal = xsellDal
        self.amzDal = amzDal
    
    def run(self):
        lAsins = self.xsellDal.getAsins()
        lAsinsRankTuple = self.amzDal.getRankForAsins(lAsins)        
        self.xsellDal.storeBsrs(lAsinsRankTuple)            
        keywords = self.xsellDal.getKeywords()
        
        prodSearchLimit = self.xsellDal.getProductSearchLimit()
        for keyword in keywords:
            time.sleep(2) 
            lAsinToRankTuple = self.getAsinRanks(prodSearchLimit, keyword, lAsins)            
            self.xsellDal.storeKeywordRank(keyword, lAsinToRankTuple)
    
    #region Private
    
    def getAsinRanks(self, prodSearchLimit, keyword, lAsins):
        dAsinToRank = self.amzDal.searchFirstNAsins(keyword, prodSearchLimit)
        
        lAsinToRankTuple = []
        for asin in lAsins:
            if asin not in dAsinToRank:
                rank = 9999
            else:
                rank = dAsinToRank[asin]
            lAsinToRankTuple.append((asin, rank))
            
        return lAsinToRankTuple
    
    #endregion