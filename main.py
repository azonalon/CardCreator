#!/bin/python
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import os
import json
import urllib
import sys
import time
from PyQt5 import QtCore, QtWidgets, QtGui, uic

class ImageLoader(QtCore.QThread):
    signalHasImage = QtCore.pyqtSignal(int)
    extensions = {"jpg", "jpeg", "png", "gif"}
    def __init__(self, imgUrl, imgType, identifier):
        QtCore.QThread.__init__(self)
        self.imgUrl = imgUrl
        self.imgType = imgType
        self.identifier = identifier

    def run(self):
        self.getImage()

    def getImage(self):
        if self.imgType not in self.extensions:
            self.imgType = "jpg"

        self.imageBytes = urllib.request.urlopen(self.imgUrl).read()
        self.signalHasImage.emit(self.identifier)


class ImageGetterWindow(QtWidgets.QWidget):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.setLayout(QtWidgets.QGridLayout())
        self.imagePixmaps = []
        self.imageLabels = []
        self.nLoading = 0
        self.imageWidgets = []
        self.loadingPixmap = QtGui.QPixmap('./giphy.gif')
        # self.sizeHint(300, 300)


    def addImage(self, raw_img):
        pm = QtGui.QPixmap()
        pm.loadFromData(raw_img)
        imageLabel = QtWidgets.QLabel(self)
        imageLabel.setPixmap(self.pm)


    def scrapeImages(self, searchtext, num_requested):
        self.initImageWidgets(num_requested)
        url = "https://www.google.co.in/search?q="+searchtext+"&source=lnms&tbm=isch"
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.loaders = {}

        imges = self.driver.find_elements_by_xpath("//div[@class='rg_meta']")
        imges = imges[0 : min(len(imges), num_requested)]
        self.nLoading = len(imges)

        print ("Total images:", len(imges), "\n")


        for i, img in enumerate(imges):
            imgUrl = json.loads(img.get_attribute('innerHTML'))["ou"]
            imgType = json.loads(img.get_attribute('innerHTML'))["ity"]
            loader = ImageLoader(imgUrl, imgType, i)
            loader.signalHasImage.connect(self.onImageLoadingFinished)
            loader.start()
            self.loaders[i] = loader
        # print( "Total downloaded: ", downloaded_img_count, "/", img_count)

    def initImageWidgets(self, nRequested):
        for i in range(nRequested):
            newWidget = QtWidgets.QLabel()
            newWidget.setPixmap(self.loadingPixmap)
            self.layout().addWidget(newWidget)
            self.imageWidgets.append(newWidget)

    def onImageLoadingFinished(self, i):
        self.nLoading -= 1
        if self.nLoading == 0:
            self.driver.quit()
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.loaders[i].imageBytes)
        self.imageWidgets[i].setPixmap(pixmap)



def main():
    app = QtWidgets.QApplication(sys.argv)
    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: win.scrapeImages("beautiful", 5))
    win = ImageGetterWindow()
    win.show()
    timer.start(200)
    app.exec_()

if __name__ == "__main__":
    main()
