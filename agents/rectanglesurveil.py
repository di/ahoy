import math
from threading import Thread
from ahoy.agent import Agent
from ahoy.event import Event

class RectangleSurveilAgent(Agent) :
    def __init__(self, uid, north_west, south_east, vel) :
       Agent.__init__(self, uid)
       self._north_west = north_west
       self._south_east = south_east
       self._vel = vel
       self._new_order = False

    def _on_order(self, event) :
        Thread(target=self._order_thread, args=(event,)).start()

    def _order_thread(self, event) :
        if event.get_node_uid() == self.get_owner_node().get_uid() :
            print self.get_owner_node().get_uid(), 'got new orders', event.get_north_west(), event.get_south_east()
            
            nw_lat, nw_lon = event.get_north_west()
            se_lat, se_lon = event.get_south_east()

            self._north_west = event.get_north_west()
            self._south_east = event.get_south_east()
            '''
            bx = math.cos(se_lat) * math.cos(se_lon-nw_lon)
            by = math.cos(se_lat) * math.sin(se_lon-nw_lon)
            mid_lat = math.atan2(math.sin(nw_lat)+math.sin(se_lat), math.sqrt((math.cos(nw_lat)+bx)*(math.cos(nw_lat)+bx) + by*by))
            mid_lon = nw_lon + math.atan2(by, math.cos(nw_lat) + bx)
            '''
            self._new_order = True
            _, _, agl = self.get_owner_node().get_position()
            self.get_owner_node().move(nw_lat, nw_lon, agl, self._vel, 0, True)
            self._new_order = False
            self._patrol()

    def _patrol(self) :
        print 'starting new patrol'
        n, w = self._north_west
        s, e = self._south_east
        movements = [ (n,w), (n,e), (s,e), (s,w) ]
        print movements

        i = 0
        while not self._new_order :
            dest = movements[i]
            print 'going to', dest
            self.get_owner_node().move(dest[0], dest[1], self.get_owner_node().get_position()[2], self._vel, 0, True)
            print 'arrived at', self.get_owner_node().get_position()
            i = (i + 1) % len(movements)

        print 'ended patrol'

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(RectangleSurveilMove, self._on_order)
        self._patrol()

class RectangleSurveilMove(Event) :
    def __init__(self, node_uid, north_west, south_east) :
        Event.__init__(self)
        self._node_uid = node_uid
        self._north_west = north_west
        self._south_east = south_east

    def get_node_uid(self) :
        return self._node_uid
    def get_north_west(self) :
        return self._north_west

    def get_south_east(self) :
        return self._south_east
