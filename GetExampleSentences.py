#!/bin/python
import lxml.etree
import requests
import queue
import sqlite3
import threading
import os
import json
from timer import timer

class AlkScraper:
    def __init__(self):
        pass
        # lxml.etree.parse("./dicts/JMdict_e")

rawDbFile = "./dicts/test.db"
def makeRawDatabase():
    exampleFile = open("./dicts/sentences.csv", "r")
    links = open("./dicts/links.csv", "r")
    if os.path.exists(rawDbFile):
        os.remove(rawDbFile)
    conn = sqlite3.connect('./dicts/test.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE sentences
              (id integer, language text, sentence text)
              """)
    c.execute("""CREATE TABLE links
              (originalId integer, translationId integer)
              """)
    for line in exampleFile:
        s = line.replace("\n", "").split('\t')
        # if(s[1] in ["deu", "eng", "jap"]):
        c.execute("insert into sentences values (?,?,?)", s)
    for line in links:
        s = line.replace("\n", "").split('\t')
        c.execute("insert into links values(?,?)", s)
    # c.execute("delete from sentences where not language in ('jpn', 'eng', 'ger')".fetchAll()
    # c.execute("delete from links where not originalId in (select id from sentences)")
    conn.commit()
    conn.close()
makeRawDatabase()

def getCols(cursor, command, *args):
    return list(zip(*cursor.execute(command, *args).fetchall()))

#%%
def getSentenceAndTranslation(i, c):
    """
    :param c: the database cursor object
    :param i: the sentence id
    """
    ids, sentences = getCols(c, """select id, sentence from sentences where id=?""", (i,))
    try:
        oids, tids = getCols(c, "select originalId, translationId from links where originalId in (?) order by originalId", ids)
        translations, langs = getCols(c, "select sentence, language from sentences where id in (%s)" % ",".join(map(str,tids)))
        return (ids[0], sentences[0], list(zip(translations, langs)))
    except ValueError:
        # no translation found
        return (ids[0], sentences[0], [])

getSentenceAndTranslation(5254848, sqlite3.connect('./dicts/test.db').cursor())


def makeRefinedDatabase():
    if os.path.exists('./dicts/examples.db'):
        os.remove("./dicts/examples.db")
    dbRaw = sqlite3.connect(rawDbFile)
    dbExamples = sqlite3.connect("./dicts/examples.db")
    cRaw = dbRaw.cursor()
    cExamples = dbExamples.cursor()
    cExamples.execute("create table examples (id integer, sentence text, translation)")
    cRaw.execute("select * from sentences where language='jpn'")
    sentences = cRaw.fetchmany(20)
    # c = sqlite3.connect("./dicts/examples.db").cursor()
    # c.execute("select * from examples").fetchall()


    nThreads = 8
    threads = []
    workerQueue = queue.Queue()
    resultQueue = queue.Queue()
    def worker():
        cRaw = sqlite3.connect(rawDbFile).cursor()
        while True:
            try:
                t = workerQueue.get_nowait()
                i, language, sentence = t
                r = getSentenceAndTranslation(i, cRaw)
                resultQueue.put(r)
                print(threading.current_thread().name, "fetched", i)
            except queue.Empty:
                resultQueue.put(None)
                break

    for x in sentences:
        workerQueue.put(x)

    for i in range(nThreads):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    nFinished = 0
    while True:
        r = resultQueue.get()
        if r is not None:
            print("Result fetched:", r[0])
            dbExamples.execute("insert into examples values (?,?,?)", (r[0], r[1], json.dumps(r[2])))
        else:
            nFinished += 1
            if nFinished is nThreads:
                break
    dbExamples.commit()
    dbExamples.close()
# makeRefinedDatabase()


if __name__ == '__main__':
    makeRefinedDatabase()
    pass
    # refineDatabase()
    # searchDatabase()
    # GetExampleSentences('無理')
