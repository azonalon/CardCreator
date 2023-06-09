from PyQt5 import QtCore, QtWidgets, QtGui
class InputField(QtWidgets.QTextEdit):
    focusLost = QtCore.pyqtSignal()
    ctrlEnterPressed = QtCore.pyqtSignal()
    itemDropped = QtCore.pyqtSignal(QtCore.QMimeData)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.updateGeometry)
    def minimumSizeHint(self):
        return QtCore.QSize(100, 33)
        # return self.maximumViewportSize()
    def sizeHint(self):
        size = self.document().size().toSize() + QtCore.QSize(1, 1)
        # print('Preferred', size.height(), size.width())
        return size
        # return QtCore.QSize(100, 100)
    def focusOutEvent(self, eventPointer):
        self.focusLost.emit()
        super().focusOutEvent(eventPointer)

    def dropEvent(self, event):
        print("something was dropped!")
        self.itemDropped.emit(event.mimeData())
    def insertFromMimeData(self, data):
        print("something was inserted!")
        self.itemDropped.emit(data)


    def keyPressEvent(self, qkeyevent):
        k = qkeyevent.key()
        m = qkeyevent.modifiers()
        if (k == QtCore.Qt.Key_Escape or k == QtCore.Qt.Key_Return) and \
            m == QtCore.Qt.ControlModifier:
            print("Control return man!")
            self.ctrlEnterPressed.emit()
        super().keyPressEvent(qkeyevent)
