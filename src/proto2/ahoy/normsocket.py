from random import randint
import pynorm
from pynorm.extra.manager import Manager, StopManager

class NormMcSocket :
    def __init__(self, ip, port) :
        self._cb = None
        self.instance = pynorm.Instance()
        
        self.session = self.instance.createSession(ip, port)
        self.session.setRxPortReuse(True, False)
        self.session.startReceiver(1024*1024)
        self.session.startSender(randint(0, 1000), 1024**2, 1400, 64, 16)
        self.stream = self.session.streamOpen(1024*1024)

        self.manager = Manager(self.instance)
        self.manager.register(pynorm.NORM_RX_OBJECT_UPDATED, self._on_rx_object_updated)
        self.manager.start()

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
    s = NormMcSocket('224.1.2.3', 12345)
    if sys.argv[1] == 'send' :
        i = 0
        while True :
            print 'sending', i
            s.send(str(i))
            i += 1
            time.sleep(1)
    else :
        s.manager.join()
