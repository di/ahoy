import sys
import socket
import struct
import time
from threading import Thread
from model import Model
from event import Event

class EventPubSub(Thread) :
    def __init__(self, ip, port) :
        Thread.__init__(self)
        self._running = True
        self._ip = ip
        self._port = port
        self._subscriptions = {}

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self._sock.bind(('', port))
        mreq = struct.pack('=4sl', socket.inet_aton(ip), socket.INADDR_ANY)

        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def subscribe(self, event_type, callback) :
        self._subscriptions[event_type] = callback

    def _process(self, data, addr) :
        typestr, modelstr = data.strip().split(' ', 1)
        if typestr in self._subscriptions.keys() :
            model = Model.from_string(modelstr)
            instance = Event(typestr, model)
            callback = self._subscriptions[typestr]
            callback(instance)

    def publish(self, event_inst) :
        self._sock.sendto('%s %s' % (event_inst.get_type(), event_inst.__str__()), (self._ip, self._port))

    def run(self) :
        while self._running :
            data, addr = self._sock.recvfrom(2048)
            self._process(data, addr)

if __name__ == '__main__' :
    def cb(event_inst) :
        print event_inst.get_model().get('something')

    ps = EventPubSub('239.192.0.100', 9998)
    ps.subscribe(sys.argv[2], cb)
    if sys.argv[1] == 'send' :
        while True :
            ps.publish(Event(sys.argv[2], Model(something='my test')))
            time.sleep(1)
    else :
        ps.start()
