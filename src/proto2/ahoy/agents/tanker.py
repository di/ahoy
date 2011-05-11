import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen


class Tanker(Agent) :
    def __init__(self, uid, forward_vel, iface, pathfile) :
        Agent.__init__(self, uid)
        self._forward_vel = forward_vel
        self._agl = 0.0; 
        self._vert_vel = 0.0; 
        self._pathfile = pathfile
        self._locs = []
        self._iface_name = iface
  
    def run(self) :
        uid = self.get_owner_node().get_uid()
        self._init_data()
        start = self._locs[3] #start ahead of the threat
        lat,lon = start.split(',')
        self._lat = lat
        self._lon = lon
        self.get_owner_node().set_position(float(lat),float(lon),self._agl)
        for l in self._locs[3:]:
            self._move(l)            


    def _init_data(self):
        f = open(self._pathfile, 'r')
        for line in f:
            line = line.rstrip('\n')
            self._locs.append(line)

        f.close()

    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self._lat = lat
        self._lon = lon
        self.get_owner_node().move(float(lat), float(lon), self._agl, self._forward_vel, self._vert_vel, True)
        self._publishmove()
    
    def _publishmove(self):
        uid = self.get_uid()
        message = str(uid) + "," + self._lat + "," + self._lon + "," + str(self._agl) + "," + str(self._forward_vel)
        m = Message(message,'*')
        self.get_owner_node().get_interface(self._iface_name).send(m, uid)
