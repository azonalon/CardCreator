from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from ExamplesList import ExamplesList
from UnixSignals import setupQuitOnSignal; setupQuitOnSignal()
import time
import platform
from selenium import webdriver
from urllib import request
from urllib.parse import unquote, quote
import json
from GetImageLinks import saveTo
import urllib

import lxml.html

# PhantomJS files have different extensions
# under different operating systems
PHANTOMJS_PATH = '/usr/bin/phantomjs'


# here we'll use pseudo browser PhantomJS,
# but browser can be replaced with browser = webdriver.FireFox(),
# which is good for debugging.
headers = {  'User-Agent':
          'Mozilla/5.0 (X11; Linux x86_64) '
          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36' }
url="https://www.google.co.in/search?q={}&source=lnms&tbm=isch"
r = request.urlopen(request.Request(url.format('ahoi'), headers=headers))
tree = lxml.html.parse(r)
f = open("./test/googlesearch.html" , "w")
tbs = [json.loads(n.text)['tu'] for n in tree.xpath("//div[contains(@class, 'rg_meta')]")]
saveTo(request.urlopen(tbs[0]).read(), "./test/tbreadtest")
f.write(lxml.html.tostring(tree, pretty_print=True).decode())
a = QtGui.QImage('./test/tbreadtest')
a.byteCount()
a.size()
a.save("./test/qimagetest.jpg")

f.close()



# for key, value in enumerate(headers):
#     webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
# browser = webdriver.PhantomJS(PHANTOMJS_PATH, )
# browser.get('https://www.google.com/search?source=ahoi')
