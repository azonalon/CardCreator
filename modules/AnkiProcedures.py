import sys; sys.path.append('/home/eduard/software/anki/')
import anki
import re
import time
import random
import sys
import http
import threading
import os
from urllib.error import HTTPError
import json
import urllib
import subprocess as sp
from .Hurigana import rubyReading
from itertools import accumulate
# b = col.getNote(notes[-9])


class HuriganaWorker():
    def __init__(self, sentences):
        super().__init__()
        self.sentences = [s.replace('\u0009', "") for s in sentences]
        self.result = None
        self.run()
    def run(self):
        joined = '\u0009'.join(self.sentences)
        split  = rubyReading(joined).split('\u0009')
        self.result = split




def updateHurigana():
    import pdb
    currDir = os.getcwd()
    ankiHome = '/home/eduard/Documents/Anki/Eduard/'
    col = anki.Collection(ankiHome + 'collection.anki2')
    notes = col.findNotes("Deck:Tango")
    split = []
    i = j = 0
    removeBrackets = lambda s: re.sub("\[\w+\]| |<.*>|\ufeff|\u200c", "", s)
    sentences = [removeBrackets(col.getNote(note)['Example Sentence'])
                           for note in notes]
    while j < len(notes):
        for l in accumulate(map(len, sentences[i:])):
            j += 1
            if l > 200:
                break
        try:
            w = HuriganaWorker(sentences[i:j])
            if len(w.result) != j - i:
                pdb.set_trace()
            split += w.result
            print("\n\nSuccess: " + str(w.result))
        except (http.client.BadStatusLine, HTTPError) as e:
            print(e)
            print('\nRequesting \n' + str(sentences[i:j]))
        i = j

    if len(split) != len(notes):
        pdb.set_trace()

    for i in range(len(notes)):
        note = col.getNote(notes[i])
        s = split[i]
        # print(s)
        note["Example Sentence"] = s
        note.flush()
    col.save()
    col.close()

if __name__ == "__main__":
    pass

def getGermanKeywords():
    col = anki.Collection("./userdata/HeisigGermanDeck.anki2")
    kanjiDeck = col.decks.allNames()[1]
    kanjiDeck = col.findNotes('Deck:"' + kanjiDeck + '"')
    kanjiDeck = list(map(col.getNote, kanjiDeck))
    kanjiDeck[300].items()
    kanjiDeck.sort(key=lambda n: int(n['Nummer (Auflage4)']))
    with open("kanjiEnglishGerman.csv", "w") as f:
        for n in kanjiDeck:
            f.write(','.join([
                n['Nummer (Auflage4)'], n['Kanji'], n['Schlüsselwort'],
                n['Englisches Schlüsselwort (6th edition)']
                ]) + "\n")


















print("ha")
