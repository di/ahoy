import socket
import struct
from threading import Thread
from ahoy.event import Event
from ahoy.events.all import All

class EventAPI :
    def __init__(self, tcp_conn=None) :
        self._subscriptions = {}
        self._running = True
        if tcp_conn == None :
            self._ip = '239.192.0.100'
            self._port = 9998
            self._setup_mc()
            self._tcp_conn = None
        else :
            self._tcp_conn = tcp_conn

    def _setup_mc(self) :
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        try :
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except :
            pass
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self._sock.bind(('', self._port))
        mreq = struct.pack('=4sl', socket.inet_aton(self._ip), socket.INADDR_ANY)

        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def publish(self, event, delay_sec=None) :
        if delay_sec == None :
            self.push_raw(event.pickle())
        else :
            Thread(tartget=self._delay, args=(event, delay_sec))

    def _delay(self, event, delay_sec) :
        pass    

    def push_raw(self, raw) :
        if self._tcp_conn == None :
            self._sock.sendto(raw, (self._ip, self._port))
        else :
            self._tcp_conn.send(struct.pack('>L', len(raw)))
            self._tcp_conn.send(raw)

    def subscribe(self, event_type, callback, **args) :
        if not self._subscriptions.has_key(event_type) :
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append((callback, args))

    def unsubscribe_all(self, event_type) :
        if self._subscriptions.has_key(event_type) :
            del self._subscriptions[event_type]

    def clear_subscriptions(self) :
        self._subscriptions = {}

    def _process(self, data) :
        event_inst = Event.from_pickle(data)
        keys = filter(lambda e : isinstance(event_inst, e), self._subscriptions.keys())
        if self._subscriptions.has_key(All) :
            keys.append(All)
        if len(keys) > 0 :
            for cb in self._subscriptions[keys[0]] :
                if len(cb[1]) > 0 :
                    cb[0](event_inst, cb[1])
                else :
                    cb[0](event_inst)

    def run(self) :
        while self._running :
            if self._tcp_conn == None :
                data, addr = self._sock.recvfrom(4096)
            else :
                data = self._tcp_assemble()
            if data != None :
                self._process(data)

    def _tcp_assemble(self) :
       length = self._tcp_conn.recv(4)
       if len(length) < 4 :
           return None
       length = struct.unpack('>L', length)[0]
       packet = self._tcp_conn.recv(length)
       while len(packet) < length :
           packet += self._tcp_conn.recv(length - len(packet))
       return packet

    def start(self) :
        t = Thread(target=self.run)
        t.start()
        return t

    def stop(self) :
        self._running = False
        if self._tcp_conn != None :
            self._tcp_conn.close()
