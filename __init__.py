#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import argparse, sys, os

def ankiMain():
    # import the main window object (mw) from aqt
    from aqt import mw

    def spawnWindow():
        win = MainWidget(None, args={'debug': False}, ankiIntegration=True)
        win.show()

    # create a new menu item, "test"
    action = QtWidgets.QAction("Create Japanese Cards", mw)
    # set it to call testFunction when it's clicked
    action.triggered.connect(spawnWindow)
    # and add it to the tools menu
    mw.menuBar().addAction(action)

def main():
    from modules.UnixSignals import setupQuitOnSignal
    setupQuitOnSignal()
    app = QtWidgets.QApplication(sys.argv)
    parser = argparse.ArgumentParser("Creates Cards for Anki")
    parser.add_argument("--debug", dest='debug', action='store_const',
                        default=False, const=True)
    args = parser.parse_args()
    # timer = QtCore.QTimer()
    # timer.setSingleShot(True)
    # timer.timeout.connect(lambda: win.scrapeImages(sys.argv[1], 5))
    win = MainWidget(app, args=args)
    # win.loadTestImages()
    win.show()
    # timer.start(0)
    app.exec_()

if __name__ == "__main__":
    from modules.MainWidget import MainWidget
    main()
else:
    from CardCreator.modules.MainWidget import MainWidget
    ankiMain()
