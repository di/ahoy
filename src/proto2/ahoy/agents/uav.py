import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from threading import Thread
from ahoy.event import Event

class UAV(Agent) :
    def __init__(self, uid, max_agl, f_vel, v_vel) :
        Agent.__init__(self, uid)
        self._forward_vel = f_vel
        self._max_agl = max_agl
        self._vert_vel = v_vel
        self._have_orders = False
        self._new_order = False

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(UAVSurveilArea, self._on_order)
        #self._wait_for_orders()
        nw = [39.913,-75.156]
        se = [39.887,-75.125]
        uid = self.get_owner_node().get_uid()
        self.get_owner_node().get_event_api().publish(UAVSurveilArea(uid,nw,se)) 

    def _on_order(self, event):
        print "Got the order"
        Thread(target=self._on_order_thread,args=(event,)).start()

    def _on_order_thread(self, event):
        if event.get_node_uid() == self.get_owner_node().get_uid():
            print self.get_owner_node().get_uid(), 'got new orders ', event.get_north_west(), event.get_south_east()
            nw_lat, nw_lon = event.get_north_west()
            se_lat, se_lon = event.get_south_east()

            self._north_west = event.get_north_west()
            self._south_east = event.get_south_east()

            self._have_orders = True
            self.get_owner_node().move(nw_lat, nw_lon,self._max_agl,self._forward_vel, self._vert_vel, True)
            #self._have_orders = False
            self._patrol()
  
    def _move(self, lat, lon, agl, fvel, vvel):
        self.get_owner_node().move(lat, lon, agl, fvel, vvel, True)

    def _wait_for_orders(self):
        while not self._have_orders:
            time.sleep(2)

    def _patrol(self):
        n,w = self._north_west
        s,e = self._south_east
        movements = [ (n,w), (n,e), (s,e), (s,w) ]
        print movements

        i = 0
        while not self._new_order :
            dest = movements[i]
            print 'going to', dest
            self.get_owner_node().move(dest[0], dest[1], self._max_agl, self._forward_vel, self._vert_vel, True)
            print 'arrived at', self.get_owner_node().get_position()
            i = (i + 1) % len(movements)

        print 'ended patrol'
        

class UAVSurveilArea(Event):
    def __init__(self,node_uid, north_west, south_east):
        Event.__init__(self)
        self._node_uid = node_uid
        self._north_west = north_west
        self._south_east = south_east
        
    def get_node_uid(self):
        return self._node_uid
    def get_north_west(self):
        return self._north_west
    def get_south_east(self):
        return self._south_east
