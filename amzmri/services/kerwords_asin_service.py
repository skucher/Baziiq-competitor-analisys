'''
Created on 11 Jun 2017

@author: sergeykucher
'''

class KeywordsAsinService(object):

    def __init__(self, amz_dal, xsell_dal):
        self.amz_dal = amz_dal
        self.xsell_dal = xsell_dal

    def run(self):
        set_words = self.xsell_dal.keywords_superset
        for asin in self.xsell_dal.our_asins:
            d_words_is_indexed = self.amz_dal.get_is_indexed_for_words(asin, set_words)
            self.xsell_dal.store_is_indexed_by_word(asin, d_words_is_indexed)
        #:
        #self.xsell_dal.our_asins        
        #self.xsell_dal.keywords_superset
        #self.xsell_dal.store_is_indexed_by_word(asin, d_words_is_indexed)