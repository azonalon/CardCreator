#!/bin/python
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import lxml
import lxml.html
from PIL import Image

im = Image.open("./Pictures/hi/ActiOn_10.png")
app = QtWidgets.QApplication([])
te = QtWidgets.QTextEdit()
te.setLayout(QtWidgets.QGridLayout())
te.document().setDefaultStyleSheet( """
    body {color: green;}
    image {max-width: 10px;}
    """)
b = QtWidgets.QPushButton('MyButton')
te.insertHtml("<body> test123 </body>")
te.insertHtml('<image><img src="./Pictures/hi/ActiOn_10.png"></image>')
print(te.toHtml())
te.layout().addWidget(b)
te.show()
app.exec_()

def addNote():
    import sys; sys.path.append('/home/eduard/software/anki/')
    import anki
    ankiHome = '/home/eduard/Documents/Anki/Heinz/'
    print('before import', sys.path)
    col = anki.Collection(ankiHome + 'collection.anki2')
    print('after import', sys.path)
    col.save()
    vocabDeck = col.decks.byName('Tango')
    vocabModel = col.models.byName("Japanese Vocabulary R&R")
    col.models.setCurrent(vocabModel)
    col.decks.select(vocabDeck['id'])
    deck = col.decks.get(vocabDeck['id'])
    deck['mid'] = vocabModel['id']
    col.decks.save(deck)
    newNote = col.newNote()
    col.cardCount()
    ## Expression
    newNote['Expression'] = '龍'
    ## Meaning
    newNote['Meaning'] = 'Drache'
    ## Reading
    newNote['Reading'] = '龍[りゅう]'
    ## Example Sentence
    newNote['Example Sentence'] = '龍は空を飛ぶ'
    ## Translation
    newNote['Translation'] = 'Der Drache steigt den Himmel hinauf.'
    ## Graphic
    newNote['Graphic']  = '<img src="dragon.jpg" />'
    if newNote.dupeOrEmpty() == 2:
        print("Card is a duplicate")
    else:
        col.addNote(newNote)
    col.close()
    #%%

def ankiTest():
    import sys; sys.path.append('/home/eduard/software/anki/')
    import anki
    ankiHome = '/home/eduard/Documents/Anki/Karl/'
    try:
        col = anki.Collection(ankiHome + 'collection.anki2')
    except:
        print("Collection is probably locked, please close Anki first.")
        return
    vocabDeck = col.decks.byName('Basic')
    col.decks.allNames()
    print(vocabDeck)
    vocabModel = col.models.byName("Basic (and reversed card)")
    print(vocabModel)
    col.models.setCurrent(vocabModel)
    col.decks.select(vocabDeck['id'])
    deck = col.decks.get(vocabDeck['id'])
    deck['mid'] = vocabModel['id']
    col.decks.save(deck)

    newNote = col.newNote()
    newNote['Front'] = 'Guess What?'
    newNote['Back'] = 'Im cool!'
    col.addNote(newNote)
    col.close()
    #%%
