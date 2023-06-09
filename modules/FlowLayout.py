#! /usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, margin=0, spacing=-1):
        super().__init__()
        self.margin = margin
        self.spacing = spacing
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            print(item.widget())
            item.widget().hide()
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin, 2 * self.margin)
        return size

    def _doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal)

            spaceY = self.spacing + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


if __name__ == '__main__':
    import sys
    class Window(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()

            flowLayout = FlowLayout()
            flowLayout.addWidget(QtWidgets.QPushButton("Short"))
            flowLayout.addWidget(QtWidgets.QPushButton("Longer"))
            flowLayout.addWidget(QtWidgets.QPushButton("Different text"))
            flowLayout.addWidget(QtWidgets.QPushButton("More text"))
            flowLayout.addWidget(QtWidgets.QPushButton("Even longer button text"))
            self.setLayout(flowLayout)
            self.setWindowTitle("Flow Layout")

    app = QtWidgets.QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit(app.exec_())
