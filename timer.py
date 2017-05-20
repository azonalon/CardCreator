import time
class Timer:
    def start(self, description=''):
        self.t1 = time.time();
        self.description=description
    def stop(self):
        t = -1000*(self.t1 - time.time())
        print(self.description, "timed: %8.fms" % t)
timer = Timer()
