import struct
import sys
import socket
from threading import Thread
from stage.eventapi import EventAPI
from stage.events.all import All

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
            data = conn.recv(4096)
            if not data :
                break
            self._api.push_raw(data)

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
