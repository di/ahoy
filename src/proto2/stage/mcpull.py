import sys
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
