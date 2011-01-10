import socket
from stage.eventapi import EventAPI
from stage.events.link import LinkEvent

class McPull :
    def __init__(self, ip, port) :
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._event_api = EventAPI((self._socket, self._ip, self._port))
        self._event_api.start()
        self._socket.sendto('init', (self._ip, self._port))

    def _on_message(self, data) :
        # A bit hacky
        self._event_api._process(data)

    def get_event_api(self) :
        return self._event_api

# Example
if __name__ == '__main__' :
    pull = McPull('127.0.0.1', 9876)
    def on_link(event) :
        if event.get_up() :
            up_str = 'UP'
        else :
            up_str = 'DOWN'
        print 'Link from %s to %s on network %s went %s' % (event.get_uid1(), event.get_uid2(), event.get_network_name(), up_str)
    pull.get_event_api().subscribe(LinkEvent, on_link)
    while True :
        pass
