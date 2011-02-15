import socket
import sys
from threading import Thread
from ahoy.events.move import EntityMoveEvent
from ahoy.events.link import LinkEvent
from ahoy.eventapi import EventAPI
from ahoy.util.geo import *

class KmlServer :
    def __init__(self, port) :
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(('', port))
        self._sock.listen(1)
        self._event_api = EventAPI()
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._event_api.subscribe(LinkEvent, self._on_link)
        self._pos = {}
        self._model_map = {}
        self._links = {}
        self._last_links = set([])
        self._first = True

    def add_model(self, uid, model, **kwds) :
        if not kwds.has_key('scale') :
            kwds['scale'] = 1
        if not kwds.has_key('heading') :
            kwds['heading'] = 0
        if not kwds.has_key('tilt') :
            kwds['tilt'] = 0
        if not kwds.has_key('roll') :
            kwds['roll'] = 0
        self._model_map[uid] = { 'model' : model, 'args' : kwds }

    def _on_move(self, event) :
        if self._pos.has_key(event.get_uid()) :
            last = self._pos[event.get_uid()][0:3]
        else :
            last = (0, 0, 0)
        self._pos[event.get_uid()] = (event.get_lat(), event.get_long(), event.get_agl() * 1000, last)

    def _on_link(self, event) :
        key = tuple(sorted([event.get_uid1(), event.get_uid2()]))
        if event.get_up() :
            self._links[key] = True
        else :
            if self._links.has_key(key) :
                del self._links[key]

    def _get_contents(self) :
        s = ''
        for uid, loc in self._pos.iteritems() :
            lat, long, agl, last = loc
            model = self._model_map[uid]['model']
            args = self._model_map[uid]['args']
            bearing = bearing_from_pts(lat, long, last[0], last[1]) - args['heading']
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
                        <heading>%s</heading>
                        <tilt>%s</tilt>
                        <roll>%s</roll>
                    </Orientation>
                    <Scale>
                        <x>%s</x>
                        <y>%s</y>
                        <z>%s</z>
                    </Scale>
                    <Link>
                        <href>%s</href>
                    </Link>
                </Model>
                </Placemark>\n''' % (uid, long, lat, agl, uid, args['heading'], args['tilt'], args['roll'], args['scale'], args['scale'], args['scale'], model)
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
                        </Orientation>
                    </Change>
                </Update>
                \n''' % (uid, long, lat, agl, uid, bearing)

        for link in self._last_links :
#            if link not in self._links :
            print 'delete', link
            s += '''
            <Update>
                <Delete>
                    <Placemark targetId="l%sto%s"></Placemark>
                </Delete>
            </Update>
            ''' % (link[0], link[1])

        self._last_links = set([])
        for id, up in self._links.iteritems() :
            if self._pos.has_key(id[0]) and self._pos.has_key(id[1]) :
                print 'add', id
                lat1, lon1, agl1 = self._pos[id[0]][0:3]
                lat2, lon2, agl2 = self._pos[id[1]][0:3]
                s += '''
                <Update>
                    <Create>
                        <Document targetId="main">
                            <Placemark id="l%sto%s">
                                <LineString>
                                    <extrude>0</extrude>
                                    <tessellate>1</tessellate>
                                    <altitudeMode>absolute</altitudeMode>
                                    <coordinates> %s,%s,%s
                                    %s,%s,%s
                                    </coordinates>
                                </LineString>
                            </Placemark>
                        </Document>
                    </Create>
                </Update>
                \n''' % (id[0], id[1], lon1, lat1, agl1, lon2, lat2, agl2)
                self._last_links.add(id)

        if self._first :
            self._first = False
            s = '<Document id="main">\n' + s + '</Document>\n'
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
        self._event_api.start()
        while True :
            conn, addr = self._sock.accept()
            Thread(target=self._handle, args=(conn,)).start()

if __name__ == '__main__' :
    server = KmlServer(int(sys.argv[1]))
    for i in range(0, 4) :
        server.add_model(i, 'file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/predator_b.dae')
    server.add_model(4, 'file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/radar.dae')
    for i in range(5, 9) :
        server.add_model(i, 'file:///Users/arosenfeld/ahoy/trunk/src/proto2/ahoy/viz/ss_united_states.dae', heading=90, scale=.3)
    server.start()
