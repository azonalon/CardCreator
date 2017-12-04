from PyQt5 import QtCore, QtWidgets, QtGui, uic
import argparse, sys, os
# moduleDirectory = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(moduleDirectory)
import modules.MainWidget

def ankiMain():
    # import the main window object (mw) from aqt
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo
    # import all of the Qt GUI library
    # from aqt.qt import *

    # We're going to add a menu item below. First we want to create a function to
    # be called when the menu item is activated.

    def testFunction():
        # get the number of cards in the current collection, which is stored in
        # the main window
        win = CardCreator.MainWidget.MainWidget(None, None)
        # win.loadTestImages()
        win.show()
        cardCount = mw.col.cardCount()
        # show a message box
        showInfo("Card count: %d" % cardCount)

    # create a new menu item, "test"
    action = QtWidgets.QAction("Create Japanese Cards", mw)
    # set it to call testFunction when it's clicked
    action.triggered.connect(testFunction)
    # and add it to the tools menu
    mw.menuBar().addAction(action)

def main():
    from CardCreator.UnixSignals import setupQuitOnSignal
    # print(searchTatoebaExamples("雨"))
    setupQuitOnSignal()
    app = QtWidgets.QApplication(sys.argv)
    parser = argparse.ArgumentParser("Creates Cards for Anki")
    parser.add_argument("--debug", dest='debug', action='store_const',
                        default=False, const=True)
    args = parser.parse_args()
    # timer = QtCore.QTimer()
    # timer.setSingleShot(True)
    # timer.timeout.connect(lambda: win.scrapeImages(sys.argv[1], 5))
    win = CardCreator.MainWidget.MainWidget(app, args=args)
    # win.loadTestImages()
    win.show()
    # timer.start(0)
    app.exec_()

if __name__ == "__main__":
    main()
else:
    ankiMain()
