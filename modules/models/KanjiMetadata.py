import sys
# sys.path.append('/home/eduard/software/anki-source/')
import re, json, os

def isChineseCharacter(c):
    return ord(c) <= 0x9FFF and ord(c) >= 0x4E00

def kanjiMetaData(kanji, col):
    assert len(kanji) == 1
    data = {}
    try:
        note = col.getNote(col.findNotes("deck:Kanji kanji:" + kanji)[0])
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
def expressionToMetadata(x, col):
    return json.dumps({'kanji': [kanjiMetaData(c, col) for c in x if isChineseCharacter(c)]},
                      indent=None, ensure_ascii=False)


def writeAllMetadata():
    model = col.models.byName("Japanese Vocabulary R&R")
    notes = col.findNotes("Deck:Tango")
    for i, note in enumerate(notes):
        n = col.getNote(note)
        print("Checking note %d/%d" % (i+1, len(notes)))
        if n.model()["id"] == model["id"]:
            n["Metadata"] = expressionToMetadata(n['Expression'], col)
            # print("Before", n["Translation"])
            n["Meaning"] = re.sub(r'\\*"', r'\"', n["Meaning"])
            n["Meaning"] = re.sub(r'<[^<>]+>', r'', n["Meaning"])
            n["Translation"] = re.sub(r'\\*"', r'\"', n["Translation"])
            n["Translation"] = re.sub(r'<[^<>]+>', r'', n["Translation"])
            # print("After", n["Translation"])
            n.flush()





if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../'))
    from anki import Collection
    ankiHome = '/home/eduard/.local/share/Anki2/Eduard/'
    col = Collection(ankiHome + 'collection.anki2')
    n = col.getNote(col.findNotes("Deck:Tango")[1002])
    dict(n)
    n["Metadata"]
    writeAllMetadata()
    col.close()
