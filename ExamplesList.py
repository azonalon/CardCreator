#!/bin/python
from GetExampleSentences import searchTatoebaExamples, AsyncAlkScraper
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from InputField import InputField
import sys

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().addWidget(QtWidgets.QLabel("Please enter Alc username"
                                                 " and password."), 0, 0, 1, 2)
        self.ue = QtWidgets.QLineEdit()
        self.layout().addWidget(self.ue, 1, 0, 1, 2)
        self.pe = QtWidgets.QLineEdit()
        self.pe.setEchoMode(QtWidgets.QLineEdit.Password)
        self.layout().addWidget(self.pe , 2, 0, 1, 2)
        bOk = QtWidgets.QPushButton("Accept")
        bOk.clicked.connect(self.onAccept)
        self.layout().addWidget(bOk, 3, 1, 1, 1)
    def onAccept(self):
        self.username = self.ue.text()
        self.password = self.pe.text()
        self.done(True)

class ExampleSentenceListModel(QtGui.QStandardItemModel):
    refitRequired = QtCore.pyqtSignal()
    def __init__(self, scrapeFunction=searchTatoebaExamples):
        super().__init__()
        self.sentences = []
        self.setRowCount(0)
        self.setColumnCount(2)
        self.alkScraper = AsyncAlkScraper()
        self.alkScraper.hasSentences.connect(self.processAlcSentences)
        self.alkScraper.needLogin.connect(self.loginToAlk)

    def loginToAlk(self):
        d = LoginDialog()
        result = d.exec_()
        if result:
            self.alkScraper.login.emit((d.username, d.password))

    def data(self, index, role):
        row, col = index.row(), index.column()
        # if role == Qt.DecorationRole:
        try:
            if role == Qt.DisplayRole or role == Qt.StatusTipRole:
                if col == 0:
                    return self.sentences[row][1]
                elif col == 1:
                    if self.sentences[row][2]:
                        return self.sentences[row][2][0][2]
        except:
            return "Error"

        # return QtGui.QIcon()

    def headerData(self, i, orientation, role):
        if role == Qt.DisplayRole:
            if i == 0:
                return "Japanese"
            if i == 1:
                return "English"

    def getTatoebaSentences(self, keyword):
        self.clearTable()
        self.sentences = searchTatoebaExamples(keyword)
        if len(self.sentences) == 0:
            print("No examples found!")
            return
        print(*self.sentences, sep='\n')
        # print(list(zip(*(self.sentences[2][2]))))
        for i, s in enumerate(self.sentences):
            if s[2] and 'eng' not in list(zip(*s[2]))[1]: # case no english
                self.sentences.remove(s)
        print("after first filter", *self.sentences, sep='\n')
        for i in range(len(self.sentences)):
            self.sentences[i][2] = [t for t in self.sentences[i][2] if t[1] == 'eng' ]
        self.updateRows()

    def updateRows(self):
        n = len(self.sentences)
        print("n: ", n)
        print(*self.sentences, sep='\n')
        self.setRowCount(n)
        self.refitRequired.emit()

    def isEmpty(self):
        return len(self.sentences) == 0

    def clearTable(self):
        self.sentences = []
        self.updateRows()

    def getAlcSentences(self, keyword):
        self.clearTable()
        self.alkScraper.requestSentences.emit(keyword)

    def processAlcSentences(self, sentences):
        self.sentences = sentences
        self.sentences = [
            [i, s[0], [[i, 'eng', s[1]]]]
            for i, s in enumerate(self.sentences)
        ]
        self.updateRows()


class ExamplesList(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ExampleSentenceListModel())
        self.horizontalHeader().sectionResized.connect(lambda *args: self.resizeRowsToContents)
        self.model().refitRequired.connect(
            lambda *args: [self.resizeRowsToContents(), self.updateGeometry(),
                           print("rows inserted!")]
        )

    def loadSentences(self, keyword, method='tatoeba'):
        if method == 'tatoeba':
            self.model().getTatoebaSentences(keyword)
        elif method == 'alc':
            self.model().getAlcSentences(keyword)
        else:
            raise ValueError("Unknown scraping method " + method)
    def sizeHint(self):
        s = self.horizontalHeader().height() + 2
        for i in range(self.model().rowCount()):
            s += self.rowHeight(i)
        return QtCore.QSize(400, s)
        # self.setItemDelegate(QtWidgets.QStyledItemDelegate())
        # self.setIconSize(QtCore.QSize(1, 1))
    def isEmpty(self):
        return self.model().isEmpty()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu("My Menu, voila!")
        menu.addAction()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QWidget()
    mw.setLayout(QtWidgets.QGridLayout())
    # s = searchTatoebaExamples("産業界")
    b = QtWidgets.QPushButton("Load Sentence")
    sl = ExamplesList()
    # sl.loadSentences("龍", method='tatoeba')
    # l = lambda: sl.loadSentences("龍", method='alc')
    # sl.show()
    b.clicked.connect(lambda: sl.loadSentences("産業界", method='alc'))
    # l = QtWidgets.QLabel("MyLabel")
    # l.setStyleSheet("background-color: yellow")
    mw.layout().addWidget(b)
    # mw.layout().addWidget(l)
    mw.layout().addWidget(sl)
    mw.show()
    app.exec_()
