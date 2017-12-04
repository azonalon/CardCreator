import sys
sys.path.append('/home/eduard/software/anki/')
import anki, re, json

def isChineseCharacter(c):
    return ord(c) <= 0x9FFF and ord(c) >= 0x4E00

def kanjiMetaData(kanji):
    assert len(kanji) == 1
    data = {}
    try:
        note = col.getNote(col.findNotes("deck:Kanji and kanji:" + kanji)[0])
        data["kunYomi"] = note["kunYomi"].split("、")
        data["onYomi"] = note["onYomi"].split("、")
        data["keyword"] = note["keyword"]
        data["heisigFrame"] = note["frameNoV4"]
        data["kanji"] = note["kanji"]
    except IndexError:
        data["kunYomi"] = ["?"]
        data["onYomi"] = ["?"]
        data["keyword"] = "???"
        data["heisigFrame"] = "?"
        data["kanji"] = "？"
    return data
def expressionToMetadata(x):
    return {'kanji': [kanjiMetaData(c) for c in x if isChineseCharacter(c)]}

if __name__ == "__main__":
    ankiHome = '/home/eduard/.local/share/Anki2/Eduard/'
    col = anki.Collection(ankiHome + 'collection.anki2')
    note = col.getNote(col.findNotes("Expression:響き渡る")[0])
    note["Metadata"] = json.dumps(expressionToMetadata(note['Expression']),
                                  indent=True)
    note.flush()
    col.close()
    with open("./AnkiCardLayout/testcard.js", "w") as f:
        f.write("var card = ")
        json.dump(dict(note), f, indent=True)
        f.close()
