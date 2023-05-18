import sys
sys.path.append('/home/eduard/software/anki/')
import anki, re, json

if __name__ == "__main__":
    ankiHome = '/home/eduard/.local/share/Anki2/Eduard/'
    col = anki.Collection(ankiHome + 'collection.anki2')
    n = col.getNote(col.findNotes("Deck:Tango")[1002])
    dict(n)
    n["Metadata"]
col.getCard(col.findCards("Deck:Takoboto tag:exported")[0])
col.close()
n.cards()
