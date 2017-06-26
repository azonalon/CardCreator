#!/bin/python
from PIL import Image
import re
import os
import sys
import lxml
import tempfile
import Hurigana
from InputField import InputField
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import argparse
from ImageScraper import ImageScraper

# QtGui.QImageWriter.supportsOption(QtGui.QImageIOHandler.Description)

f = open('./imageViewer_ui.py', 'w')
uic.compileUi('./imageViewer.ui', f)
f.close()
import imageViewer_ui
uiImageLoader = imageViewer_ui.Ui_Form


class MainWidget(QtWidgets.QWidget, uiImageLoader):
    colors = {"warning": "#f2e394",
              "error"  : "#f2ae72",
              "white"  : "#FFFFFF"}
    imageMaxWidth = 400
    def __init__(self, app, args):
        super(QtWidgets.QWidget, self).__init__()
        # self.col = None
        self.setupUi(self)
        self.col = self.getCollection()
        # self.imageList.setIconSize(QtCore.QSize(200, 200))
        self.stagedPictures = {}
        self.args = args
        self.inputFields = [self.teExpression, self.teMeaning,
                            self.teReading, self.teExampleSentence,
                            self.teTranslation, self.tePicture]
        # self.readingGenerator = ReadingGenerator()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.initUi)
        self.timer.setSingleShot(True)
        self.timer.start(0)
        self.initHandlers()

        app.aboutToQuit.connect(self.clearFields)

    def onItemDropped(self, data):
        print("Where in main dropped function!")
        if data.hasImage():
            print("Picture in Drop!")
            self.insertPicture(data.imageData())
        elif data.hasText():
            self.sender().insertPlainText(data.text())

    def initHandlers(self):
        # self.bSearchImage.clicked.connect(self.getImages)
        self.bAddNote.clicked.connect(self.addNote)
        for field in self.inputFields:
            field.ctrlEnterPressed.connect(self.addNote)
            field.itemDropped.connect(self.onItemDropped)
        self.teExpression.focusLost.connect(lambda: self.checkNote(self.makeNote()))
        # self.bTakeFromList.clicked.connect(self.takeImageFromList)
        self.bExpressionAddReading.clicked.connect(
            lambda: self.addReading(self.teExpression,
                                    self.teReading)
            )
        self.bExampleSentenceAddReadings.clicked.connect(
            lambda: self.addReading(self.teExampleSentence,
                                    self.teExampleSentence)
            )
        self.cbExampleSearchMethod.setItemData(0, "alc")
        self.cbExampleSearchMethod.setItemData(1, "tatoeba")
        self.bSearchExampleSentence.clicked.connect(self.searchExamples)
        self.examplesList.customContextMenuRequested.connect(self.examplesListCustomContextMenuEvent)

    def insertExampleSentence(self, sentence, translation):
        self.teTranslation.append(translation)
        self.teExampleSentence.append(sentence)

    def examplesListCustomContextMenuEvent(self, pos):
        menu = QtWidgets.QMenu("My menu, ha!")
        action = QtWidgets.QAction("Use in note")
        row = self.examplesList.indexAt(pos).row()
        print(row)
        if row == -1:
            return
        sentence = self.examplesList.model().index(row, 0).data()
        translation = self.examplesList.model().index(row, 1).data()
        action.triggered.connect(
            lambda: self.insertExampleSentence(sentence, translation)
        )
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())

    def searchExamples(self):
        method = self.cbExampleSearchMethod.currentData()
        print(method)
        self.examplesList.loadSentences(self.teExpression.toPlainText(), method=method)

    def addReading(self, sourceEdit, targetEdit):
        expression = sourceEdit.toPlainText()
        expression = re.sub(r"\[\w*\]", "", expression)
        # print(expression, len(expression))
        result = Hurigana.reading(expression, method='ruby')
        result = re.sub(r"\]", "] ", result)
        targetEdit.setHtml(result)

    def initUi(self):
        if self.args.debug:
            self.teExpression.insertHtml("龍")
            self.teMeaning.insertHtml('Drache')
            self.teReading.insertPlainText('')
            self.teExampleSentence.insertHtml('龍は空を飛ぶ')
            self.teTranslation.insertHtml('Der Drache steigt den Himmel hinauf.')
            self.insertPicture(open('dragon.jpg', 'rb').read(), 'jpg', 'dragon')

    def getCollection(self):
        if 'anki' not in globals():
            import sys; sys.path.append('/home/eduard/software/anki/')
            import anki
            ankiHome = '/home/eduard/Documents/Anki/Eduard/'
            try:
                col = anki.Collection(ankiHome + 'collection.anki2')
                ### changes cwd to /path/to/collection.media/
                return col
            except Exception as e:
                self.infoMessage("Collection is probably locked, please close Anki first.")
                raise e
                return None
        else:
            global mw
            return mw.col
    def closeCollection(self):
        print("Finalizing the collection...")
        self.col.close()

    def makeNote(self):
        vocabDeck = self.col.decks.byName('Tango')
        vocabModel = self.col.models.byName("Japanese Vocabulary R&R")
        self.col.models.setCurrent(vocabModel)
        self.col.decks.select(vocabDeck['id'])
        deck = self.col.decks.get(vocabDeck['id'])
        deck['mid'] = vocabModel['id']
        self.col.decks.save(deck)
        newNote = self.col.newNote()
        self.col.cardCount()
        newNote['Expression']       = self._escapeHtml(self.teExpression.toHtml())
        newNote['Meaning']          = self._escapeHtml(self.teMeaning.toHtml())
        newNote['Reading']          = self._escapeHtml(self.teReading.toHtml())
        newNote['Example Sentence'] = self._escapeHtml(self.teExampleSentence.toHtml())
        newNote['Translation']      = self._escapeHtml(self.teTranslation.toHtml())
        newNote['Graphic']          = self._escapeHtml(self.tePicture.toHtml())
        return newNote

    def clearFields(self):
        self.teExpression.setHtml('')
        self.teMeaning.setHtml('')
        self.teReading.setPlainText('')
        self.teExampleSentence.setHtml('')
        self.teTranslation.setHtml('')
        self.tePicture.setHtml('')
        # for f in self.stagedPictures.keys():
            # os.remove(f)


    def checkNote(self, note):
        isValid = True
        # print("Expression:", note['Expression'])
        # print("Expression html:", self.teExpression.toHtml())
        # print('stylesheet', self.tePicture.styleSheet())
        if note is None:
            return
        elif note.dupeOrEmpty() == 1:
            self.infoMessage('Expression must not be empty.')
            self.teExpression.setStyleSheet("background-color: " + self.colors['warning'] + ";")
            isValid = False
            isValid = False
        elif note.dupeOrEmpty() == 2:
            self.infoMessage('The Expression field is a duplicate.')
            self.teExpression.setStyleSheet("background-color: " + self.colors['error'] + ";")
            isValid = False
        else:
            self.teExpression.setStyleSheet("background-color: " + self.colors['white'] + ";")
            self.infoMessage('Card Valid.')
        return isValid

    # def takeImageFromList(self):
    #     item = self.lwImages.currentItem()
    #     self.insertPicture(item.imageBytes, item.type, item.name)

    def insertPicture(self, qimage):
        # f = io.BytesIO(rawBytes)
        # im = Image.open(f)
        # w, h = im.size
        # aspect = w/h
        # wr = min(w, self.imageMaxWidth)
        # hr = round(wr/aspect)
        # if wr < w:
        #     im = im.resize((wr, hr), resample=Image.LANCZOS)
        imageType = 'jpg'
        newName = os.path.basename(
            tempfile.mkstemp(prefix='pic_', dir='.')[1] )

        qimage.save(newName + '.' + imageType)
        self.stagedPictures[newName + '.' + imageType] = qimage
        self.tePicture.insertHtml('<img src="%s.%s" class="Image"/>' % (newName, imageType))

    def saveStagedPictures(self, note):
        tree = lxml.html.fromstring(self.tePicture.toHtml())
        imgs = tree.xpath('//img/@src')
        leftovers = set(imgs) - set(self.stagedPictures.keys())
        for img in leftovers:
            os.remove(img)
        self.stagedPictures = {}


    def addNote(self):
        newNote = self.makeNote()
        if self.checkNote(newNote):
            self.saveStagedPictures(newNote)
            self.col.addNote(newNote)
            self.infoMessage("Note added.")
            self.col.save()
            self.clearFields()

    def infoMessage(self, str):
        self.leInfo.setText(str)

    # def getImages(self):
    #     source = self.cbSearchSource.currentText()
    #     self.lwImages.clear()
    #     query = {'Custom': self.leCustomQuery.text(),
    #              'Expression': self.teExpression.toPlainText(),
    #              'Meaning': self.teMeaning.toPlainText()
    #              }[source]
    #     count = 10
    #     self.imageLoader.requestImages(query, count)

    # def onImageAcquired(self, imageBytes, imageType, name):
    #     self.lwImages.addItem(PictureItem(imageBytes, imageType, name))
    #
    # def loadTestImages(self):
    #     import glob
    #     for f in glob.glob('./Pictures/hi/*.jpg'):
    #         self.lwImages.addItem(PictureItem(open(f, 'rb').read(), f), 'jpg', 'name')

    def _escapeHtml(self, htmlString):
        """
        Takes the output of QTextEdit.toHtml() and strips the outer
        html tags for output to Anki notes
        """
        tree = lxml.html.fromstring(htmlString)
        inner = tree.xpath('/html/body/p')
        body = inner[0]
        result =  (body.text or '') + \
            ''.join([lxml.html.tostring(child, method='xml', encoding='unicode')
                     for child in body.iterchildren()])
        if result == '<br/>':
            return ""
        return result


def main():
    from UnixSignals import setupQuitOnSignal
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
    win = MainWidget(app, args=args)
    # win.loadTestImages()
    win.show()
    # timer.start(0)
    app.exec_()

if __name__ == "__main__":
    main()
