# Your code here
def setupQuitOnSignal():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
# Your code here.
