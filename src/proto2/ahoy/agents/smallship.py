import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen


class SmallShip(Agent) :
    def __init__(self, uid, dataid, forward_vel,pathfile) :
        Agent.__init__(self, uid)
        self._forward_vel = forward_vel
        self._agl = 0.0; 
        self._vert_vel = 0.0; 
        #self._pathfile = "/home/frank/ahoy/src/proto2/ahoy/agents/paths.txt"
        self._pathfile = pathfile
        self._locs = []
        self._dataid = dataid

    def run(self) :
        uid = self.get_owner_node().get_uid()
        self._init_data()
        start = self._locs[0]
        lat,lon = start.split(',')
        self.get_owner_node().set_position(float(lat),float(lon),self._agl)
        for l in self._locs[1:]:
            self._move(l)            


    def _init_data(self):
        f = open(self._pathfile, 'r')
        for line in f:
            line = line.rstrip('\n')
            self._locs.append(line)

        f.close()

    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self.get_owner_node().move(float(lat), float(lon), self._agl, self._forward_vel, self._vert_vel, True)

