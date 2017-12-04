#!/bin/python
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from .ExamplesList import ExamplesList
from .UnixSignals import setupQuitOnSignal; setupQuitOnSignal()
import time
import platform
from selenium import webdriver
from urllib import request
from urllib.parse import unquote, quote
import json
import urllib
import lxml.html
from .timer import Timer, qtStartHook

class MyThread(QtCore.QThread):
    def __init__(self):
        super().__init__()
    def run():
        pass

app = QtWidgets.QApplication([])
thread = QtCore.QThread()
thread.started.connect(lambda: print("thread start"))
thread.finished.connect(lambda: print("thread finished"))
t1 = qtStartHook(thread.start)
t2 = qtStartHook(thread.exit, 1000)
app.exec_()
