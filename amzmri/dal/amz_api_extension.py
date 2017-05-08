'''
Created on 3 May 2017

@author: sergeykucher
'''
from amazon.api import AmazonAPI, AmazonSearch, NoMorePages, RequestThrottled
from itertools import islice
import time
from urllib2 import HTTPError

class AmazonAPIExt(AmazonAPI):
    
    def __init__(self, aws_key, aws_secret, aws_associate_tag, **kwargs):
        super(AmazonAPIExt, self).__init__(aws_key, aws_secret, aws_associate_tag, **kwargs)
        
    def search_n(self, n, **kwargs):
        """Search and return first N results..

        :param n:
            An integer specifying the number of results to return.
        :return:
            A list of :class:`~.AmazonProduct`.
        """
        region = kwargs.get('region', self.region)
        kwargs.update({'region': region})
        items = AmazonSearchExt(self.api, self.aws_associate_tag, **kwargs)
        try:
            return list(islice(items, n))
        except Exception, e:
            keywords = kwargs.get('Keywords')
            print "FAILED %s - %s - %s" % (str(keywords),str(e),type(e))
            return []
    
    
class AmazonSearchExt(AmazonSearch):
    def __init__(self, api, aws_associate_tag, **kwargs):
        super(AmazonSearchExt, self).__init__(api, aws_associate_tag, **kwargs)
        
    def lookup(self, ResponseGroup="Large", **kwargs):
        num_times = 5
        for i in xrange(1, num_times):
            try:
                return super(AmazonSearchExt, self).lookup(ResponseGroup="Large", **kwargs)                
            except (RequestThrottled, HTTPError) as e:
                time.sleep(0.5 * i) 
                print "Failed %d - error:%s - lookup:%s" % (i,str(e),str(self.kwargs))
                continue
        raise Exception('%d attempts is not enough' % num_times)
        
        
        
    def iterate_pages(self):
        """Iterate Pages.

        A generator which iterates over all pages.
        Keep in mind that Amazon limits the number of pages it makes available.

        :return:
            Yields lxml root elements.
        """
        try:
            while True:
                    for i in xrange(1,5):
                        try:
                            root = self._query(ItemPage=self.current_page, **self.kwargs)
                            break
                        except (RequestThrottled, HTTPError) as e:
                            time.sleep(0.5 * i) 
                            print "Failed %d - error:%s - query:%s" % (i,str(e),str(self.kwargs))
                            continue
                        
                    if(root is None):
                        raise Exception('5 attempts is not enough for')
                    
                    yield root                        
                    self.current_page += 1                
        except NoMorePages:
            pass