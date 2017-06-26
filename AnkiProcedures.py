import sys; sys.path.append('/home/eduard/software/anki/')
import anki
import re
from Hurigana import rubyReading
ankiHome = '/home/eduard/Documents/Anki/Eduard/'
col = anki.Collection(ankiHome + 'collection.anki2')
notes = col.findNotes("Deck:Tango")
b = col.getNote(notes[-9])
b.fields
for n in notes:
    note = col.getNote(n)
    s = note['Example Sentence']
    s = re.sub("\[\w+\]| ", "", s)
    s = rubyReading(s)
    print(s)
    note["Example Sentence"] = s
    note.flush()
col.save()
col.close()
