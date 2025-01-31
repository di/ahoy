import socket
import sys
import signal
from ahoy.eventapi import EventAPI
from ahoy.events.link import LinkEvent
from ahoy.events.move import EntityMoveEvent

class SdtInterface :
    def __init__(self, ip, port, sdt_port) :
        # Socket to local SDT instance
        self._sdt_port = sdt_port
        self._sdt_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Socket to remote simulation event channel
        self._remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_sock.connect((ip, port))
        self._event_api = EventAPI(self._remote_sock)
        t = self._event_api.start()
        self._event_api.subscribe(LinkEvent, self._on_link)
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        t.join()

    def _send(self, msg) :
        print 'To SDT:', msg
        self._sdt_sock.sendto(msg, ('127.0.0.1', self._sdt_port))

    def _on_radar(self, event) :
        lat, lon, agl = event.get_radar_loc()
        self._send('node %s position %s,%s,%s' % (event.get_sensor_id(), lon, lat, agl))

    def _on_link(self, event) :
        if event.get_up() :
            thickness = 3#max(1, int(8 * (1-(event.get_pathloss() / -100))))
            self._send('link %s,%s,%s line %s,%s' % (event.get_uid1(), event.get_uid2(), '802.11', 'red', thickness))
        else :
            self._send('delete link,%s,%s,%s' % (event.get_uid1(), event.get_uid2(), '802.11'))

    def _on_move(self, event) :
        self._send('node %s position %s,%s,%s' % (event.get_uid(), event.get_long(), event.get_lat(), int(event.get_agl() * 1000)))

if __name__ == '__main__' :
    if len(sys.argv) < 3 :
        print '    usage: python %s <remote_ip> <remote_port> <local_sdt_port>' % sys.argv[0]
        sys.exit(0)

    pull = SdtInterface(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    def quit(signal, frame) :
        print 'Stopping...'
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)
