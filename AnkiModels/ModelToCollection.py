if __name__ == "__main__":
    ankiHome = '/home/eduard/.local/share/Anki2/Eduard/'
    col = anki.Collection(ankiHome + 'collection.anki2')
    myModel = col.models.byName("Japanese Vocabulary R&R")
    note = col.getNote(col.findNotes("Expression:響き渡る")[0])
    note["Metadata"] = json.dumps(expressionToMetadata(note['Expression']),
                                  indent=True)
