import socket
import sys
from stage.mcpull import McPull
from stage.events.link import LinkEvent
from stage.events.move import EntityMoveEvent

class SdtPull(McPull) :
    def __init__(self, ip, port) :
        McPull.__init__(self, ip, port)
        self._sdt_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.get_event_api().subscribe(LinkEvent, self._on_link)
        self.get_event_api().subscribe(EntityMoveEvent, self._on_move)

    def _on_link(self, event) :
        if event.get_up() :
            self._sdt_sock.send('link %s,%s,%s line %s,%s' % (event.get_uid1(), event.get_uid2(), '802.11', 'red', '3'))
        else :
            self._sdt_sock.send('delete link %s,%s,%s' % (event.get_uid1(), event.get_uid2(), '802.11'))

    def _on_move(self, event) :
        self._sdt_sock.send('node %s position %s,%s,%s' % (event.get_uid(), event.get_long(), event.get_lat(), event.get_agl()))

if __name__ == '__main__' :
    if len(sys.argv) < 3 :
        print '    usage: python mcpull <remote_ip> <remote_port> <local_sdt_port>'
        sys.exit(0)

    pull = SdtPull(sys.argv[1], int(sys.argv[2]))
    while True :
        pass
