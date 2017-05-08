import os
import urllib
import urllib2

from amazon.api import AmazonAPI
from bs4 import BeautifulSoup

class Extractor(object):
    def __init__(self, accessKey, secretKey, tag):
        self._amazonApi = AmazonAPI(accessKey, secretKey, tag)

    def extractPictures(self, lAsins, targetDir):
        products = self._getProducts(lAsins, "Images")
        self._getImages(products, targetDir)

    def _getImages(self, products, targetDir):
        for product in products:
            productDir = os.path.join(targetDir, product.asin)
            if not os.path.exists(productDir):
                os.makedirs(productDir)
            for i, image in enumerate(product.images):
                imagUrl = image.LargeImage.URL.text
                fileName = os.path.join(productDir, "%d.jpg" % i)
                urllib.urlretrieve(imagUrl, fileName)

    def _getProducts(self, lAsins, responceGroup):
        products = []
        chunks = Extractor.chunks(lAsins, 10)
        for chunk in chunks:
            sChunk = ",".join(chunk)
            currProducts = self._amazonApi.lookup(ItemId=sChunk, ResponseGroup=responceGroup)
            if isinstance(currProducts, list):
                products.extend(currProducts)
            else:
                products.append(currProducts)
        return products

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def extractTitles(self, lAsins):
        products = self._getProducts(lAsins, "Small")
        return self._getTitles(products)

    def extractBullets(self, lAsins):
        products = self._getProducts(lAsins, "Large")
        return self._getBullets(products)

    def _getBullets(self, products):
        res = []
        for p in products:
            res.append("---- {0} ----\n".format(p.asin.encode('utf8')))
            for feature in p.features:
                res.append("    {0}\n".format(feature.encode('utf8')))
        return res

    def extractProductDescriptions(self, lAsins):
        products = self._getProducts(lAsins, "Large")
        return self._getProductDescriptions(products)

    def _getProductDescriptions(self, products):
        res = []
        for p in products:
            res.append("\n")
            res.append("---- {0} ----\n".format(p.asin.encode('utf8')))
            res.append("    {0}\n".format(p.editorial_review.encode('utf8')))
        return res

    def extractTitlesBySearch(self, search):
        products = self._search(search)
        return self._getTitles(products)

    def _getTitles(self, products):
        return ["{0},{1}\n".format(p.asin, p.title.encode('utf8')) for p in products]


    def extractBulletsBySearch(self, search):
        products = self._search(search)
        return self._getBullets(products)

    def extractImagesBySearch(self, search, targetDir):
        products = self._search(search)
        self._getImages(products, targetDir)

    def extractProductDescriptionsBySearch(self, search):
        products = self._search(search)
        return self._getProductDescriptions(products)

    def _search(self, search):
        return list(self._amazonApi.search_n(25, ResponseGroup="Large", Keywords=search, SearchIndex='All'))


    def extractReviews(self, search, starsRange, targetDir):

        products = self._search(search)

        for star in starsRange:
            startsStr = self._converStars(star)
            fileName = os.path.join(targetDir, "{0}.csv".format(startsStr))
            res = []
            for product in products:
                res.append("---- {0} ----\n".format(product.asin.encode('utf8')))
                soup = self._getProductReviewSoup(product, startsStr)
                reviews = soup.findAll('span',{'class' : lambda x: x and 'review-text' in x})
                res.extend(["   - {0}\n".format(review.text.encode('utf8')) for review in reviews])
            with open(fileName, mode='w') as f:
                    f.writelines(res)
                    f.close()

    def extractReviewPictures(self, search, starsRange, targetDir):

        products = self._search(search)
        for product in products:
            for star in starsRange:
                startsStr = self._converStars(star)
                soup = self._getProductReviewSoup(product, startsStr)
                reviewImages = soup.findAll('img',{'alt' : lambda x: x and 'review image' in x})
                productDir = os.path.join(targetDir, startsStr, product.asin)
                if len(reviewImages) == 0:
                    continue
                if not os.path.exists(productDir):
                    os.makedirs(productDir)
                for i, image in enumerate(reviewImages):
                    imagUrl = image.attrs['src'].encode('utf8')
                    fileName = os.path.join(productDir, "review-%d.jpg" % i)
                    urllib.urlretrieve(imagUrl, fileName)

    def _getProductReviewSoup(self, product, startsStr):
        url = '''http://www.amazon.com/product-reviews/%s/?filterByStar=%s''' % (product.asin, startsStr)
        try:
            f = urllib2.urlopen(url)
            page = f.read();
        except:
            page = ""
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def _converStars(self, numStars):
        if numStars == 1:
            return "one_star"
        if numStars == 2:
            return "two_star"
        if numStars == 3:
            return "three_star"
        if numStars == 4:
            return "four_star"
        if numStars == 5:
            return "five_star"
        raise NotImplemented()