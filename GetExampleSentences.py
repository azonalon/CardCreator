#!/bin/python
import lxml.html as html
import lxml
import requests
import queue
import sqlite3
import threading
import os
import json
import re
from timer import timer
import urllib.request as request
from urllib.parse import urlparse, urlencode, quote, unquote
from PyQt5 import QtCore, QtWidgets


# __file__ = os.getcwd() + "lksdjfls.py"
dictsPath = os.path.dirname(__file__) + '/dicts/'
dictsPath
examplesDb = dictsPath + "examples.db"
rawDbFile = dictsPath + "sentencesAndLinks.db"



def saveTo(sourceBytes, target):
    with open(target, 'wb') as f:
        f.write(sourceBytes)

def getResponseCookiesString(requestResult):
    cookies = [t[1].split(';')[0] for t in requestResult.getheaders()
               if t[0] == 'Set-Cookie' ]
    cookies = '; '.join(cookies)
    return cookies
#%%


class AsyncAlkScraper(QtCore.QThread):
    requestSentences = QtCore.pyqtSignal(str)
    hasSentences = QtCore.pyqtSignal(list)
    needLogin = QtCore.pyqtSignal()
    login = QtCore.pyqtSignal(tuple)
    loginFinished = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.worker = AlkScraper()
        self.loggedIn = False
        self.start()

    def onRequest(self, q):
        if self.loggedIn:
            self.hasSentences.emit(self.worker.searchExamples(q))
        else:
            self.needLogin.emit()

    def onLogin(self, usernamePassword):
        try:
            self.worker.login(usernamePassword)
            self.loggedIn = True
            self.loginFinished.emit(True)
        except:
            self.loginFinished.emit(False)

    def run(self):
        self.requestSentences.connect(self.onRequest)
        self.login.connect(self.onLogin)
        # self.started.connect()
        self.exec_()

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

class AlkScraper(QtCore.QObject):
    # urlparse(alcLoginFormData)
    alcQueryUrl = "http://eowpf.alc.co.jp/search?q="

    def __init__(self):
        super().__init__()

    def login(self, usernamePassword = None):
        if usernamePassword is not None:
            self.alcLoginFormData = urlencode({"username": usernamePassword[0],
                                               "password": usernamePassword[1],
                                               "login-form-type": "pwd"
                                               })

        loginUrl = "https://eowpf.alc.co.jp/pkmslogin.form?token=Unknown"
        req = request.Request(loginUrl, data=self.alcLoginFormData.encode(),
                              method='POST')
        result = request.urlopen(req)
        # print(*result.getheaders(), sep='\n')
        cookies = getResponseCookiesString(result)

        if not 'LtpaToken2' in cookies:
            print("Wrong Login to Alc!")
            raise Exception("Wrong login Data")

        print('cookies A', cookies)

        req2 = request.Request(self.alcQueryUrl + "%E6%AF%8D",
                               headers={'Cookie': cookies}, method='POST')
        result2 = request.urlopen(req2)
        cookies += "; " + getResponseCookiesString(result2)
        print('cookies B', cookies)
        print("logged in")
        self.cookies = cookies

    def searchExamples(self, query):
        print("lookin for sentences!!!")
        try:
            s = (self.getSentences(self.getResultList(query)))
            return s
        except:
            return []

    def getResultList(self, query):
        query = quote(query)
        req = request.Request(self.alcQueryUrl + query, headers={'Cookie': self.cookies}, method='POST')
        result = request.urlopen(req)
        # saveHtml(result, "./test/alcquery2.html")
        tree = html.parse(result)
        # print(lxml.etree.tostring(tree))
        return tree.xpath("//div[@id='resultlist']")[0]

    def getSentences(self, resultList):
        sentences = []
        for i in range(len(resultList)):
            try:
                translation = resultList[i][1][0].xpath("./text()")[0][:-1]
                original  = "".join([r.text for r in resultList[i][0].xpath("./span[@class='redtext']")] + resultList[i][0].xpath('./text()'))
                original = re.sub("[\n\r\t\s]", "", original)
                sentences.append((original, translation))
            except:
                pass
        return sentences

def makeIndicesDatabase():
    os.remove("./dicts/japaneseIndices.db")
    db = sqlite3.connect("./dicts/japaneseIndices.db")
    c = db.cursor()
    c.execute("create table indices (jpnId integer, engId integer, sentence text)")
    indicesSource = open("./dicts/jpn_indices.csv")
    for line in indicesSource:
        s = line.replace("\n", "").split('\t')
        c.execute("insert into indices values (?,?,?)", s)
    db.commit()


def makeRawDatabase():
    exampleFile = open("./dicts/sentences.csv", "r")
    links = open("./dicts/links.csv", "r")
    if os.path.exists(rawDbFile):
        os.remove(rawDbFile)
    conn = sqlite3.connect(rawDbFile)
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
# makeRawDatabase()

def getCols(cursor, command, *args):
    result =  list(zip(*cursor.execute(command, *args).fetchall()))
    return result

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



def getMemoryDatabase(origDbCursor):
    """ :param args: list of tables to copy """
    mdb = sqlite3.connect(":memory:")
    c = mdb.cursor()
    tables = origDbCursor.execute('select name, sql from sqlite_master').fetchall()
    for name, definition in tables:
        print(name)
        c.execute(definition)
        rows = origDbCursor.execute('select * from ' + name).fetchall()
        nColumns = len(rows[0])
        pattern = '(' + ','.join(['?'] * nColumns) + ')'
        c.executemany('insert into ' + name + ' values ' + pattern, rows)
    mdb.commit()
    return mdb
# b = getMemoryDatabase(sqlite3.connect('./dicts/examples.db').cursor())
# b = getMemoryDatabase(sqlite3.connect(rawDbFile).cursor())
# b.execute("select * from links").fetchall()

def getTranslations(i, c):
    """
    :param c: the database cursor object
    :param i: the sentence id
    """
    # i=5254848; c = sqlite3.connect(rawDbFile).cursor()
    return c.execute("""select id, language, sentence from sentences
                    where id in (select translationId from links
                        where originalId=? )""",  (i,)).fetchall()

def makeRefinedDatabase():
    if os.path.exists('./dicts/examples.db'):
        os.remove("./dicts/examples.db")
    dbRaw = sqlite3.connect(rawDbFile)
    dbExamples = sqlite3.connect("./dicts/examples.db")
    cRaw = dbRaw.cursor()
    cExamples = dbExamples.cursor()
    cExamples.execute("create table examples (id integer, sentence text, translation)")
    cRaw.execute("select * from sentences where language='jpn'")
    sentences = cRaw.fetchall()
    n = len(sentences)
    # c = sqlite3.connect("./dicts/examples.db").cursor()
    # c.execute("select * from examples").fetchall()


    nThreads = 4
    threads = []
    workerQueue = queue.Queue()
    resultQueue = queue.Queue()
    def worker():
        # cRaw = getMemoryDatabase(sqlite3.connect(rawDbFile).cursor()).cursor()
        cRaw = sqlite3.connect(rawDbFile).cursor()
        while True:
            try:
                t = workerQueue.get_nowait()
                i, language, sentence = t
                r = getTranslations(i, cRaw)
                resultQueue.put((i, sentence, r))
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
    i = 0
    eta = -1
    timer.start()
    while True:
        r = resultQueue.get()
        if r is not None:
            i += 1;
            dbExamples.execute("insert into examples values (?,?,?)", (r[0], r[1], json.dumps(r[2])))
            print("Result fetched: id", r[0], "%d/%d eta %4.1fstd" % (i, n, eta))
        else:
            nFinished += 1
            if nFinished is nThreads:
                break

        if i % 100 == 0:
            dt = timer.stop() / 1000 / 60 / 60
            eta = (n - i)/(100 / dt)
            timer.start()
    dbExamples.commit()
    dbExamples.close()
    timer.stop()

def searchTatoebaExamples(query):
    print("cwd", os.getcwd())
    c = sqlite3.connect(examplesDb).cursor()
    try:
        results = c.execute("select * from examples where sentence like '%%%s%%'" % query).fetchall()
        results = [[*result[0:2], json.loads(result[2])] for result in results]
    except ValueError:
        return []
    return results


if __name__ == '__main__':
    from UnixSignals import setupQuitOnSignal; setupQuitOnSignal()
    app = QtCore.QCoreApplication([])
    s = AlkScraper()
    s.login(('sauter.eduard@gmail.com', 'amt1415'))
    # qtimer = QtCore.QTimer()
    # qtimer.setSingleShot(True)
    # qtimer.timeout.connect(lambda: s.requestSentences.emit("龍"))
    # qtimer.start(20)
    # app.exec_()
    # print(s.searchExamples("ごめんなさい"))
    # print(s.searchExamples("heureka"))
    # print(s.searchExamples("午後ご午後"))
    # print(searchTatoebaExamples("産業界"))
    # print(searchTatoebaExamples("龍"))
    # pass
    # makeRawDatabase()
    # makeRefinedDatabase()
