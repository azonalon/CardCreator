#!/bin/python
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import os
import json
import urllib
import sys
import time
import reading
from PyQt5 import QtCore, QtWidgets, QtGui, uic


f = open('./imageViewer_ui.py', 'w')
uic.compileUi('./imageViewer.ui', f)
f.close()
uiImageLoader, baseClass = uic.loadUiType('./imageViewer.ui')

class ImageLoader(QtCore.QThread):
    extensions = {"jpg", "jpeg", "png", "gif"}
    def __init__(self, imgUrl, imgType):
        QtCore.QThread.__init__(self)
        self.imgUrl = imgUrl
        self.imgType = imgType

    def run(self):
        self.getImage()

    def getImage(self):
        if self.imgType not in self.extensions:
            self.imgType = "jpg"

        try:
            self.imageBytes = urllib.request.urlopen(self.imgUrl).read()
        except:
            self.imageBytes = open('./giphy', 'rb').read()
            pass


def scrapeImages(searchText, nRequested):
    url = "https://www.google.co.in/search?q="+searchText+"&source=lnms&tbm=isch"
    driver = webdriver.Chrome()
    driver.get(url)

    imges = driver.find_elements_by_xpath("//div[@class='rg_meta']")
    imges = imges[0 : min(len(imges), nRequested)]

    print ("Total images:", len(imges), "\n")
    imgUrls = [json.loads(img.get_attribute('innerHTML'))["ou"] for img in imges]
    imgTypes = [json.loads(img.get_attribute('innerHTML'))["ity"] for img in imges]
    driver.quit()
    return zip(imgUrls, imgTypes)




class ImageGetterWindow(QtWidgets.QWidget, uiImageLoader, QtCore.QObject):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        QtCore.QObject.__init__(self)
        self.setupUi(self)
        # self.imageList.setIconSize(QtCore.QSize(200, 200))
        self.imagePixmaps = []
        self.imageLabels = []
        self.nLoading = 0
        self.nAcquired = 0
        self.bFetchImages.clicked.connect(
            lambda: self.scrapeImages(self.leFetchImages.text(), 5)
        )
        self.loadingPixmap = QtGui.QPixmap('./giphy.gif')
        self.loaders = {}

    def scrapeImages(self, searchText, nRequested):
        self.initImageWidgets(nRequested)
        imges = scrapeImages(searchText, nRequested)
        for i, (imgUrl, imgType) in enumerate(imges):
            print(imgUrl, imgType)
            loader = ImageLoader(imgUrl, imgType)
            loader.finished.connect(self.onImageLoadingFinished)
            loader.start()
            self.loaders[i] = loader


    def initImageWidgets(self, nRequested):
        for i in range(nRequested):
            newIcon = QtGui.QIcon(self.loadingPixmap)
            self.imageList.addItem(
                QtWidgets.QListWidgetItem(newIcon, "")
            )

    def onImageLoadingFinished(self):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.sender().imageBytes)
        self.imageList.item(self.nAcquired).setIcon(QtGui.QIcon(pixmap))
        self.nAcquired += 1



def main():
    app = QtWidgets.QApplication(sys.argv)
    # timer = QtCore.QTimer()
    # timer.setSingleShot(True)
    # timer.timeout.connect(lambda: win.scrapeImages(sys.argv[1], 5))
    win = ImageGetterWindow()
    win.show()
    # timer.start(0)
    app.exec_()

if __name__ == "__main__":
    main()
