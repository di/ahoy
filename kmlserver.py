import socket
import sys
from threading import Thread
from ahoy.events.move import EntityMoveEvent
from ahoy.eventapi import EventAPI

class KmlServer :
    def __init__(self, port, model_map) :
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(('', port))
        self._sock.listen(1)
        self._event_api = EventAPI()
        self._event_api.start()
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._pos = {}
        self._model_map = model_map
        self._first = True

    def _on_move(self, event) :
        self._pos[event.get_uid()] = (event.get_lat(), event.get_long(), event.get_agl())

    def _get_contents(self) :
        s = ''
        for uid, loc in self._pos.iteritems() :
            lat, long, agl = loc
            model = self._model_map[uid]
            if self._first :
                s += '''<Placemark>
                <Model>
                <altitudeMode>absolute</altitudeMode>
                <Location id="%s">
                <longitude>%s</longitude>
                <latitude>%s</latitude>
                <altitude>%s</altitude>
                </Location>
                <Link>
                <href>%s</href>
                </Link>
                </Model>
                </Placemark>\n''' % (uid, long, lat, agl, model)
            else :
                s += '''
                <Update>
                <Change>
                <Location targetId="%s">
                    <longitude>%s</longitude>
                    <latitude>%s</latitude>
                    <altitude>%s</altitude>
                </Location>
                </Change>
                </Update>
                \n''' % (uid, long, lat, agl)

        if self._first :
            self._first = False
            s = '<Document>\n' + s + '</Document>\n'
        else :
            s = '<NetworkLinkControl>\n' + s + '</NetworkLinkControl>\n'
        return s

    def _handle(self, conn) :
        data = 'HTTP/1.1 200 OK\n'
        data += 'Content-Type: application/vnd.google-earth.kml+xml\n\n'
        contents = self._get_contents()
        if contents != None :
            data += '<?xml version="1.0" encoding="UTF-8"?>\n'
            data += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
            data += contents
            data += '</kml>'
            conn.send(data)
            print data
            print '\n'
        conn.close()

    def start(self) :
        while True :
            conn, addr = self._sock.accept()
            Thread(target=self._handle, args=(conn,)).start()

if __name__ == '__main__' :
    mapping = {}
    for i in range(0, 10) :
        mapping[i] = 'file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/ss_united_states.dae'
    KmlServer(int(sys.argv[1]), mapping).start()
