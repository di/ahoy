import socket
import struct
from threading import Thread
from stage.event import Event

class EventAPI(Thread) :
    def __init__(self) :
        Thread.__init__(self)
        self._subscriptions = {}
        self._ip = '239.192.0.100'
        self._port = 9998
        self._setup_mc()
        self.start()

    def _setup_mc(self) :
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self._sock.bind(('', self._port))
        mreq = struct.pack('=4sl', socket.inet_aton(self._ip), socket.INADDR_ANY)

        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def publish(self, event) :
        self._sock.sendto(event.pickle(), (self._ip, self._port))

    def subscribe(self, event_type, callback, **args) :
        if not self._subscriptions.has_key(event_type) :
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append((callback, args))

    def unsubscribe_all(self, event_type) :
        if self._subscriptions.has_key(event_type) :
            del self._subscriptions[event_type]

    def _process(self, data) :
        event_inst = Event.from_pickle(data)
        keys = filter(lambda e : isinstance(event_inst, e), self._subscriptions.keys())
        if len(keys) > 0 :
            print 'Processing %s ' % event_inst
            for cb in self._subscriptions[keys[0]] :
                if len(cb[1]) > 0 :
                    cb[0](event_inst, cb[1])
                else :
                    cb[0](event_inst)

    def run(self) :
        while True :
            data, addr = self._sock.recvfrom(2048)
            # TODO: thread this line?
            self._process(data)
