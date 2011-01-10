import socket
from threading import Thread
from stage.eventapi import EventAPI
from stage.events.all import All

class McPush :
    def __init__(self, port) :
        self._api = EventAPI()
        self._api.start()
        self._api.subscribe(All, self._on_event)
        self._port = port
        self._clients = set([])

        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._listen_sock.bind(('', self._port))
        Thread(target=self._listener).start()

        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _listener(self) :
        while True :
            data, addr = self._listen_sock.recvfrom(2048)
            if data == 'init' :
                print 'New connection from %s' % (addr,)
                self._clients.add(addr)
            else :
                #print 'Forwarding event from %s' % (addr,)
                self._api.push_raw(data)

    def _on_event(self, event) :
        #print 'Pushing event:'
        for client in self._clients :
            try :
                #print '    %s' % (client,)
                self._send_sock.sendto(event.pickle(), client)
            except :
                #print '    %s : error' % (client,)
                self._client.discard(client)
