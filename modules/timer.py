import time
from PyQt5 import QtCore
class Timer:
    def start(self, description=''):
        self.t1 = time.time();
        self.description=description
    def stop(self):
        t = -1000*(self.t1 - time.time())
        print(self.description, "timed: %8.fms" % t)
        return t
timer = Timer()

def qtStartHook(f, delay=0):
    t = QtCore.QTimer()
    t.setSingleShot(True)
    t.timeout.connect(f)
    t.start(delay)
    return t
