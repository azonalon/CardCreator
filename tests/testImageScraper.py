import sys
print(sys.path)
from modules.ImageScraper import ImageScraper
from PyQt5 import QtCore, QtGui, QtWidgets

print("hello world")
app = QtWidgets.QApplication([])
area = QtWidgets.QScrollArea()
area.setWidgetResizable(True)
# area.setFixedHeight(400)
scraper = ImageScraper()
area.setWidget(scraper)
scraper.startScrape("stars", 10)
area.show()
app.exec_()
