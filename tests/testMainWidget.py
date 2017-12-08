import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5 import QtCore, QtWidgets, QtGui, uic
# moduleDirectory = os.path.dirname(os.path.abspath(__file__))
moduleDirectory = './modules'
f = open(moduleDirectory + '/imageViewer_ui.py', 'w')
uic.compileUi(moduleDirectory + '/imageViewer.ui', f, from_imports=True)
f.close()
from modules.MainWidget import MainWidget

app = QtWidgets.QApplication([])
mw = MainWidget(app, [])
mw.teExpression.setText("暴露")
mw.bSearchImage.click()
mw.show()
app.exec_()
