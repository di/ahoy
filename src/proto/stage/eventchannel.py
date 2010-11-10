import sys
import socket
import struct
from threading import Thread
from events import *

class EventPubSub(Thread) :
    def __init__(self, ip, port) :
        Thread.__init__(self)
        self._running = True
        self._mc_addr = (ip, port)
        self._subscriptions = {}

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self._sock.bind(('', port))
        mreq = struct.pack('=4sl', socket.inet_aton(ip), socket.INADDR_ANY)

        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def subscribe(self, event, callback) :
        self._subscriptions[event.EVENT_ID] = callback

    def _process(self, data, addr) :
        typestr, modelstr = data.strip().split(' ', 1)
        etype = event_from_id[typestr]
        if etype in self._subscriptions.keys() :
            model = Model.from_string(modelstr)
            instance = etype(model)
            callback(instance)

    def send(self, data) :
        self._sock.sendto(data, self._mc_addr)

    def run(self) :
        while self._running :
            data, addr = self._sock.recvfrom(2048)
            self._process(data, addr)

if __name__ == '__main__' :
    ps = EventPubSub('239.192.0.100', 9998)
    ps.start()
    ps.subscribe(TestEvent)
