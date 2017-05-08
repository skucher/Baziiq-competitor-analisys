'''
Created on 9 Aug 2016

@author: sergeykucher
'''

class AmzDalMock(object):
    
    def __init__(self):
        self.dKeywordAsins = {}
        self.lAsinRanks = []
        
    def searchFirstNAsins(self, keyword, prodSearchLimit):        
        return self.dKeywordAsins[keyword]
    
    def getRankForAsins(self, lAsins):
        return self.lAsinRanks
    