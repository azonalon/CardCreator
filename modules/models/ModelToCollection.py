import sys, json
sys.path.append('/home/eduard/software/anki/')
import anki
from shutil import copy
import os, glob
from lxml.html import fromstring
from lxml.etree import tostring

if __name__ == "__main__":
    ankiHome = '/home/eduard/.local/share/Anki2/Eduard/'
    for f in glob.glob("*.ttf"):
        copy(f, os.path.join(ankiHome, "collection.media", f))

    recognition = fromstring(open("Recognition.html", "r").read())
    recall = fromstring(open("Recall.html", "r").read())
    back = fromstring(open("Back.html", "r").read())
    stylesheet = open("ModelStyle.css", "r").read()


    jsHeader = """var card = {
     'Expression': '{{Expression}}',
     'Meaning': "{{Meaning}}",
     'Reading': '{{Reading}}',
     'Example Sentence': '{{Example Sentence}}',
     'Translation': "{{Translation}}",
     'Graphic': '{{Graphic}}',
     'Metadata': '{{Metadata}}'
 }
 """
    jsScript = "<script>\n" + jsHeader + open("ModelScript.js").read() + "\n</script>\n"

    col = anki.Collection(ankiHome + 'collection.anki2')
    myModel = col.models.byName("Japanese Vocabulary R&R")
    backNode = back.xpath("/html/body/div[@class='card']")[0]
    recognitionNode = recognition.xpath("/html/body/div[@class='card']")[0]
    recallNode = recall.xpath("/html/body/div[@class='card']")[0]

    myModel['css'] = stylesheet # stylesheet goes here

    assert myModel['tmpls'][0]['name'] == "Recognition"
    myModel['tmpls'][0]['qfmt'] = tostring(recognitionNode).decode() + jsScript # frontside html body goes here
    myModel['tmpls'][0]['afmt'] = tostring(backNode).decode() + jsScript# backside html body goes here

    assert myModel['tmpls'][1]['name'] == "Recall"
    myModel['tmpls'][1]['qfmt'] = tostring(recallNode).decode() + jsScript# frontside html body goes here
    myModel['tmpls'][1]['afmt'] = tostring(backNode).decode() + jsScript# backside html body goes here

    col.models.flush()
    col.models.save()
    col.close()
