import sys; sys.path.append('/home/eduard/software/anki/')
import anki
import re
import time
import sys
import http
import threading
from urllib.error import HTTPError
import json
import urllib
import subprocess as sp
from Hurigana import rubyReading
# b = col.getNote(notes[-9])

removeBrackets = lambda s: re.sub("\[\w+\]| |<.*>", "", s)
partOfList = lambda i, j: [removeBrackets(col.getNote(note)['Example Sentence'])
                       for note in notes[i:j]]

class HuriganaWorker():
    def __init__(self, sentences):
        super().__init__()
        self.sentences = sentences
        self.result = None
    def run(self):
        try:
            joined = ';'.join(self.sentences)
            split  = rubyReading(joined).split(';')
            self.result = split
            print(json.dumps(split))
            sys.exit(0)
        except (http.client.BadStatusLine, HTTPError) as e:
            sys.exit(1)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        w = HuriganaWorker(json.loads(sys.argv[1]))
        w.run()

    ankiHome = '/home/eduard/Documents/Anki/Eduard/'
    col = anki.Collection(ankiHome + 'collection.anki2')
    notes = col.findNotes("Deck:Tango")
    i = 0
    split = []
    while i < len(notes):
        try:
            s = partOfList(50 * i, 50 * (i+1))
            w = sp.run(['python', './AnkiProcedures.py', json.dumps(s)],
                        check=True)
            result = json.loads(w.stdout)
            print("got result", result)
            split += w.result
            i += 1
        except:
            continue

    print(split)
    sys.exit(0)
    for i in range(len(notes)):
        note = col.getNote(notes[i])
        s = split[i]
        print(s)
        note["Example Sentence"] = s
        note.flush()
        time.sleep(60 * 10)
    col.save()
    col.close()
