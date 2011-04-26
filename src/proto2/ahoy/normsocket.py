from random import randint
from pynorm.extra.manager import Manager, StopManager
import pynorm

class NormMcSocket :
    def __init__(self, ip, port) :
        self._cb = None
        instance = pynorm.Instance()
        session = instance.createSession(ip, port)
        session.setRxPortReuse(True, False)
        session.startReceiver(1024*1024)
        session.startSender(randint(0, 1000), 1024**2, 1400, 64, 16)
        self.stream = session.streamOpen(1024*1024)
        manager = Manager(instance)
        manager.register(pynorm.NORM_RX_OBJECT_UPDATED,
            lambda e: self._on_rx_object_updated(e))

    def _on_rx_object_updated(self, event) :
        print 'recv:', event.object

    def send(self, data) :
        self.stream.streamWrite(data)
        self.stream.streamFlush(True)

    def set_recv_cb(self, fn) :
        self._recv_cb = fn

if __name__ == '__main__' :
    import time
    import sys
    s = NormMcSocket('239.1.2.3', 12345)
    if sys.argv[1] == 'send' :
        i = 0
        while True :
            print 'sending', i
            s.send(str(i))
            i += 1
            time.sleep(1)

    else :
        while True :
            pass
