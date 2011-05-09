import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen
from ahoy.events.move import EntityMoveEvent
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.util.geo import *

class ThreatShip(Agent) :
    def __init__(self, uid, forward_vel, pathfile) :
        Agent.__init__(self, uid)
        self._forward_vel = forward_vel
        self._agl = 0.001; 
        self._vert_vel = 0.0; 
        self._pathfile = pathfile
        self._locs = []
        self._follow = None

    def follow(self, nodeid):
        self._follow = nodeid

    def run(self) :
        uid = self.get_owner_node().get_uid()
        self._init_data()
        start = self._locs[0]
        lat,lon = start.split(',')
        self.get_owner_node().set_position(float(lat),float(lon),self._agl)
        if(self._follow != None):
            self.get_owner_node().get_event_api().subscribe(EntityMoveEvent, self._on_tanker_move)

        print 'Threat at ' + lat + ',' + lon
        for l in self._locs[1:]:
            print 'Threat moving to ' + l
            self._move(l)            


    def _init_data(self):
        f = open(self._pathfile, 'r')
        for line in f:
            line = line.rstrip('\n')
            self._locs.append(line)

        f.close()

    def _on_tanker_move(self, event):
        if event.get_uid() == self._follow:
            print 'Got the follow event'
            lat = event.get_lat()
            lon = event.get_long()
            vel = event.get_forward_vel()
            mylat,mylon,myagl = self.get_owner_node().get_position()
            d = lin_distance(lat,lon,0.0,mylat,mylon,0.0)
            print str(d) + ' kilos away'
            if d == 0 :
                print 'Intercepted ship'
                self.get_owner_node().get_event_api().publish(ChemicalSpillEvent(self.get_owner_node().get_position(), .0002))
            elif d <= 0.2 and vel != 0 :
                print 'Slowing down...'
                self._forward_vel = vel
            elif d > 0.2 :
                print 'Speeding up...'
                self._forward_vel = vel + 0.08         
            
            self.get_owner_node().set_forward_velocity(self._forward_vel)
            
    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self._curlat = float(lat)
        self._curlon = float(lon)
        self.get_owner_node().move(float(lat), float(lon), self._agl, self._forward_vel, self._vert_vel, True)

