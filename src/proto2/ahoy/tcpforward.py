import struct
import sys
import socket
from threading import Thread
from ahoy.eventapi import EventAPI
from ahoy.events.all import All

class TcpForward :
    def __init__(self, port) :
        self._api = EventAPI()
        self._api.start()
        self._api.subscribe(All, self._on_event)
        self._clients = set([])

        self._tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server.bind(('', port))
        self._tcp_server.listen(1)

        Thread(target=self._acceptor).start()

    def _acceptor(self) :
        while True :
            conn, addr = self._tcp_server.accept()
            self._clients.add(conn)
            Thread(target=self._listener, args=(conn,))

    def _listener(self, conn) :
        while True :
            print 'got data'
            length = conn.recv(4)
            if len(length) < 4 :
                return None
            length = struct.unpack('>L', length)[0]
            packet = conn.recv(length)
            while len(packet) < length :
                packet += conn.recv(length - len(packet))
            self._api.push_raw(packet)

    def _on_event(self, event) :
        discards = set([])
        for client in self._clients :
            try :
               raw = event.pickle()
               client.sendall(struct.pack('>L', len(raw)))
               client.sendall(raw)
            except :
                print 'error sending:', sys.exc_info()[0]
                discards.add(client)

        for discard in discards :
            self._clients.discard(discard)
