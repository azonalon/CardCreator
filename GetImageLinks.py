#!/bin/python
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import urllib
import os
import json
import sys
import time
from timer import timer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, pyqtSignal, QObject
from PyQt5.QtWebEngineWidgets import QWebEnginePage
import lxml.html
from urllib.parse import quote


header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}


class GetDynamicHtml(QObject):
    sigHtmlAvailable = pyqtSignal(str)
    def __init__(self):
        super().__init__()
    def getHtml(self, url):
        self.app = QApplication(sys.argv)
        self.page = QWebEnginePage()
        self.page.load(QUrl(url))
        self.page.loadFinished.connect(self.onLoadFinished)
        self.app.exec_()
    def onLoadFinished(self):
        f = open('duckduck.html', 'w')
        self.page.toHtml(lambda x: [f.write(x), f.close(),
                                    self.sigHtmlAvailable.emit(x),
                                    self.app.exit(0)])



class ImageLinkFetcher(QObject):
    sigLinksReady = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def requestImageLinks(self, query, number, engine='google'):
        """ Queries Google for image links.
        :param query: The keywords to search for.
        :param number: The maximum number of links to return.
        :returns: A list of tuples (imageUrl, imageType)
        """
        self.number = number
        {'google': self.searchGoogle,
        'duckduckgo': self.searchDuckDuckGo}.get(engine)(query)

    def parseDuckDuckGoHtml(self, htmlstr):
        htmlstr = open('./duckduck.html', 'r').read() if htmlstr else htmlstr
        tree = lxml.html.fromstring(htmlstr)
        thumbnails = tree.xpath('//img[@class="tile--img__img  js-lazyload"]/@src')
        thumbnails = list(map(html.unescape, thumbnails))
        self.sigLinksReady.emit(list(zip(thumbnails, ['jpg'] * len(thumbnails))))

    def searchDuckDuckGo(self, query):
        query= query.split()
        query='+'.join(query)
        url="https://www.duckduckgo.com/?q="+query+"&t=h_&iar=images&iax=1&ia=images"
        getHtml = GetDynamicHtml()
        getHtml.sigHtmlAvailable.connect(self.parseDuckDuckGoHtml)
        getHtml.getHtml(url)

    def searchGoogle(self, query):
        query= query.split()
        query='+'.join(query)
        query = quote(query)
        url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
        # print(url)
        timer.start()
        data = urllib.request.urlopen(urllib.request.Request(url, headers=header)).read()
        timer.stop()
        timer.start()
        # strainer = SoupStrainer("div",{"class":"rg_meta"})
        # soup = BeautifulSoup(data, 'lxml', parse_only=strainer)
        tree = lxml.html.fromstring(data)
        timer.stop()
        ActualImages=[]# contains the link for Large original images, type of  image
        timer.start()
        links = tree.xpath('//div[@class="rg_meta"]')
        for a in links:
            # print(a)
            link, Type =json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            ActualImages.append((link,Type))
        timer.stop()

        # print  ("there are total" , len(ActualImages),"images")
        self.sigLinksReady.emit(ActualImages)


if __name__=='__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    fetcher = ImageLinkFetcher()
    # fetcher.sigLinksReady.connect(lambda x: print(x))
    fetcher.requestImageLinks(sys.argv[1], 5, engine=sys.argv[2])
    # query = 'tree'
    # url="https://www.duckduckgo.com/?q="+query+"&t=h_&iar=images&iax=1&ia=images"
    # print(getHtml.getHtml(url))
    #This step is important.Converting QString to Ascii for lxml to process
    # archive_links = html.fromstring(str(result.toAscii()))
    # print (result)
    # getImageLinks("beautiful", 5, engine='duckduckgo')
