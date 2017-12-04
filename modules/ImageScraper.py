#!/bin/python
import requests
import re
import urllib
import os
import json
import sys
import time
from .timer import timer
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QUrl, pyqtSignal, QObject
from PyQt5.QtWebEngineWidgets import QWebEnginePage
import lxml.html
import urllib.request as request
from urllib.parse import urlparse, urlencode, quote, unquote
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from .FlowLayout import FlowLayout
from . import MainWidget


def saveTo(sourceBytes, target):
    with open(target, 'wb') as f:
        f.write(sourceBytes)


header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36" }
googleApiKey = "AIzaSyDoDZ1pbEvPHwFiWwfpjb8TPSXvRdNNuQo"

class DownloadSpeedError(Exception):
    pass
class AbortionError(Exception):
    pass

class ProgressImageLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setPixmap(QtGui.QPixmap('./media/loading.jpg'))
        self.menu=None

    def mouseReleaseEvent(self, ev):
        if self.menu:
            self.menu.exec(ev.globalPos())

    def copyImage(self):
        MainWidget.mw.insertPicture(self.image)

    def setProgress(self, percentage):
        pass

    def setFinal(self, qImage):
        self.image = qImage
        self.menu = QtWidgets.QMenu("Image selected")
        self.moveImage = QtWidgets.QAction("Copy to note")
        self.moveImage.triggered.connect(self.copyImage)
        self.menu.addAction(self.moveImage)
        self.setPixmap(QtGui.QPixmap.fromImage(qImage))


class ImageScraper(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: white")
        self.setLayout(FlowLayout())
        self.setAutoFillBackground(True)
        self.query = ''
        self.nWorkers = 8
        self.nAcquired = 0
        self.workerThreads = {}

    def clear(self):
        self.layout().__del__()

    def startScrape(self, keyword, nMax, method='google'):
            self.linkIter = ImageLinkFetchers.searchGoogle(keyword)
            self.nMax = nMax
            self.nAcquired = 0
            for i in range(self.nWorkers):
                thread = QtCore.QThread()
                worker = ImageScraperWorker(None)
                worker.moveToThread(thread)
                thread.started.connect(worker.downloadImage)
                worker.finished.connect(thread.exit)
                thread.finished.connect(self.onWorkerExit)
                label = ProgressImageLabel()
                self.layout().addWidget(label)
                worker.madeProgress.connect(label.setProgress)
                thread.start()
                self.workerThreads[thread] = (worker, thread, label)

    def abort(self):
        for worker, thread, label in self.workerThreads.items():
            worker.abort()

    def onWorkerExit(self):
        # print("In worker exit", QtCore.QThread.currentThreadId())
        # print("Sender:", self.sender())
        sender = self.sender()
        if not sender:
            #TODO understand why sender can be None
            return
        worker, thread, label = self.workerThreads[sender]
        if worker.qImage is not None:
            label.setFinal(worker.qImage)
            self.nAcquired += 1
        if self.nAcquired < self.nMax:
            try:
                worker.imageLink, imageType = next(self.linkIter)
            except urllib.error.URLError:
                # TODO: handle network connection fail
                pass
            thread.start()
        else:
            try:
                del self.workerThreads[self.sender()]
            except:
                pass


class ImageScraperWorker(QtCore.QObject):
    madeProgress = pyqtSignal(float)
    finished = pyqtSignal()
    def __init__(self, imageLink):
        super(QtCore.QObject, self).__init__()
        self.imageLink = imageLink
        self.qImage = None
        self.shouldQuit = False

    def abort(self):
        self.shouldQuit = True

    def downloadImage(self):
        print("Downloading image", self.imageLink)
        try:
            if self.imageLink is None:
                raise AbortionError
            self.lastTime = time.time()
            f, headers = urllib.request.urlretrieve(
                self.imageLink,
                reporthook=self.urlretrieveReportHook)
            self.qImage = QtGui.QImage(f)
        except (DownloadSpeedError, AbortionError)as e:
            pass
        print("Exit download",  self.imageLink)
        self.finished.emit()

    def urlretrieveReportHook(self, blocknum, blocksize, filesize):
        if self.shouldQuit:
            raise AbortionError
        timePassed = time.time() - self.lastTime
        bps = blocksize/timePassed
        eta = filesize/bps
        if eta > 10:
            print("Download Takes too long!")
            raise DownloadSpeedError
        elif eta > 0.5:
            self.madeProgress.emit(blocknum * blocksize / filesize)
        print("Eta", eta, "bps", bps, "filesize", filesize)
        self.lastTime = time.time()


class ImageLinkFetchers(object):
    # sigLinksReady = pyqtSignal(list)
    # def __init__(self):
        # super().__init__()

    # def requestImageLinks(self, query, number, engine='google'):
    #     """ Queries Google for image links.
    #     :param query: The keywords to search for.
    #     :param number: The maximum number of links to return.
    #     :returns: A list of tuples (imageUrl, imageType)
    #     """
    #     self.number = number
    #     {'google': self.searchGoogle,
    #     'duckduckgo': self.searchDuckDuckGo}.get(engine)(query)

    def parseDuckDuckGoHtml(self, htmlstr):
        htmlstr = open('./duckduck.html', 'r').read() if htmlstr else htmlstr
        tree = lxml.html.fromstring(htmlstr)
        thumbnails = tree.xpath('//img[@class="tile--img__img  js-lazyload"]/@src')
        thumbnails = list(map(unquote, thumbnails))
        self.sigLinksReady.emit(list(zip(thumbnails, ['jpg'] * len(thumbnails))))

    def searchDuckDuckGo(self, query):
        query= query.split()
        query='+'.join(query)
        url="https://www.duckduckgo.com/?q="+query+"&t=h_&iar=images&iax=1&ia=images"
        getHtml = self.GetDynamicHtml()
        getHtml.sigHtmlAvailable.connect(self.parseDuckDuckGoHtml)
        getHtml.getHtml(url)


    def searchGoogle(query, loadThumbnail=True):
        # TODO: use 'forward' 'scroll' and 'start' to maybe get more images
        query = query.split(' ')
        query = quote('+'.join(query), encoding='utf-8')
        url="https://www.google.co.jp/search?q="+query+"&source=lnms&tbm=isch"
        r = urllib.request.urlopen(urllib.request.Request(url, headers=header))
        tree = lxml.html.parse(r)
        links = tree.xpath('//div[contains(@class, "rg_meta")]')
        for a in links:
            if loadThumbnail:
                yield json.loads(a.text)["tu"], 'jpg'
            else:
                yield json.loads(a.text)["ou"], json.loads(a.text)["ity"]
