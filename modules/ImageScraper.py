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


header={'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        'Accept-Language': 'ja', 'Referer': 'https://www.google.co.jp/'}
# googleApiKey = "AIzaSyDoDZ1pbEvPHwFiWwfpjb8TPSXvRdNNuQo"

class DownloadSpeedError(Exception):
    pass
class AbortionError(Exception):
    pass

class ProgressImageLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setPixmap(QtGui.QPixmap('./media/loading.jpg'))
        self.menu=None
        self.setScaledContents(True)

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
        self.setPixmap(QtGui.QPixmap.fromImage(qImage.scaledToWidth(100)))


class ImageScraper(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.setStyleSheet("background-color: white")
        self.spacing = 5
        # self.setLayout(FlowLayout(spacing=self.spacing))
        # self.setAutoFillBackground(True)
        self.query = ''
        self.nWorkers = 8
        self.nAcquired = 0
        self.workers = [ImageScraperWorker(None) for _ in range(self.nWorkers)]
        for w in self.workers:
            w.finished.connect(self.onWorkerExit)
        self.setLayout(FlowLayout(spacing=self.spacing))
        self.lock = QtCore.QMutex()

    def clear(self):
        self.layout().__del__()
        # for w in self.layout().widgets():
        #     self.layout().removeWidget(w)
        self.setStyleSheet("background-color:black;")

    def startScrape(self, keyword, nMax, method='google'):
            self.linkIter = ImageLinkFetchers.searchGoogle(keyword, loadThumbnail=False)
            self.nMax = nMax
            self.nAcquired = 0
            for w in self.workers:
                w.abort()
                w.imageLink = None
            for w in self.workers:
                w.wait()
                w.start()

    def abort(self):
        for worker, thread, label in self.workerThreads.items():
            worker.abort()

    def onWorkerExit(self):
        print("In worker exit", QtCore.QThread.currentThreadId())
        print("Sender:", self.sender())
        worker = self.sender()
        if not worker:
            #TODO understand why sender can be None
            return
        if worker.qImage is not None:
            self.nAcquired += 1
            label = ProgressImageLabel()
            self.layout().addWidget(label)
            label.setFinal(worker.qImage)
        if self.nAcquired < self.nMax:
            try:
                self.lock.lock()
                worker.imageLink, imageType = next(self.linkIter)
                self.lock.unlock()
            except urllib.error.URLError:
                # TODO: handle network connection fail
                pass
            worker.start()


class ImageScraperWorker(QtCore.QThread):
    madeProgress = pyqtSignal(float)
    def __init__(self, imageLink):
        super(QtCore.QObject, self).__init__()
        self.imageLink = imageLink

    def run(self):
        self.qImage = None
        self.shouldQuit=False
        self.downloadImage()

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
            print("Aborting...", self.imageLink)
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass
            print("Link not found, aborting...")

    def urlretrieveReportHook(self, blocknum, blocksize, filesize):
        if self.shouldQuit:
            raise AbortionError
        timePassed = time.time() - self.lastTime
        bps = blocksize/timePassed
        eta = filesize/bps
        if eta > 100:
            print("Download Takes too long! eta:%4.2fs" % eta)
            raise DownloadSpeedError
        elif eta > 0.5:
            self.madeProgress.emit(blocknum * blocksize / filesize)
        print("Eta", eta, "bps", bps, "filesize", filesize)
        self.lastTime = time.time()


class ImageLinkFetchers(object):
    def searchGoogle(query, loadThumbnail=True):
        # TODO: use 'forward' 'scroll' and 'start' to maybe get more images
        query = query.split(' ')
        query = quote('+'.join(query), encoding='utf-8')
        url="https://www.google.co.jp/search?q="+query+"&source=lnms&tbm=isch"
        url="https://www.google.co.jp/search?q="+query+"&source=lnms&tbm=isch&sa=X&ved=0ahUKEwj2y4arm_rXAhURUlAKHZXwDg8Q_AUICigB&biw=700&bih=1102"
        r = urllib.request.urlopen(urllib.request.Request(url, headers=header))
        tree = lxml.html.parse(r)
        links = tree.xpath('//div[contains(@class, "rg_meta")]')
        for a in links:
            if loadThumbnail:
                yield json.loads(a.text)["tu"], 'jpg'
            else:
                yield json.loads(a.text)["ou"], json.loads(a.text)["ity"]
