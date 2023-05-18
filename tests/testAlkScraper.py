import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.GetExampleSentences import AlkScraper
from PyQt5 import QtCore, QtGui, QtWidgets

scraper = AlkScraper()
scraper.login(("sauter.eduard@gmail.com", "amsrt1415"))
print(scraper.searchExamples("龍"))
