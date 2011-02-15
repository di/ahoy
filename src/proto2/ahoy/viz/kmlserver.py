import socket
import sys
from threading import Thread
from ahoy.events.move import EntityMoveEvent
from ahoy.eventapi import EventAPI
from ahoy.util.geo import *

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
        if self._pos.has_key(event.get_uid()) :
            last = self._pos[event.get_uid()][0:3]
        else :
            last = (0, 0, 0)
        self._pos[event.get_uid()] = (event.get_lat(), event.get_long(), event.get_agl(), last)

    def _get_contents(self) :
        s = ''
        for uid, loc in self._pos.iteritems() :
            lat, long, agl, last = loc
            model, rotate = self._model_map[uid]
            bearing = bearing_from_pts(lat, long, last[0], last[1]) - rotate
            print uid, bearing
            if self._first :
                s += '''<Placemark>
                <Model>
                    <altitudeMode>absolute</altitudeMode>
                    <Location id="%s">
                        <longitude>%s</longitude>
                        <latitude>%s</latitude>
                        <altitude>%s</altitude>
                    </Location>
                    <Orientation id="o%s">
                        <heading>0.0</heading>
                        <tilt>0.0</tilt>
                        <roll>0.0</roll>
                    </Orientation>
                    <Link>
                        <href>%s</href>
                    </Link>
                </Model>
                </Placemark>\n''' % (uid, long, lat, agl, uid, model)
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
                <Update>
                    <Change>
                        <Orientation targetId="o%s">
                            <heading>%s</heading>
                            <tilt>0.0</tilt>
                            <roll>0.0</roll>
                        </Orientation>
                    </Change>
                </Update>
                \n''' % (uid, long, lat, agl, uid, bearing)

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
        conn.close()

    def start(self) :
        while True :
            conn, addr = self._sock.accept()
            Thread(target=self._handle, args=(conn,)).start()

if __name__ == '__main__' :
    mapping = {}
    for i in range(0, 4) :
        mapping[i] = ('file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/predator_b.dae', 0)
    mapping[4] = ('file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/radar.dae', 0)
    for i in range(5, 9) :
        mapping[i] = ('file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/ss_united_states.dae', 90)
    KmlServer(int(sys.argv[1]), mapping).start()
