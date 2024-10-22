import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen
from threading import Thread

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
        if(len(self._locs) >= 4):
            start = self._locs[3] #start ahead of the threat
        else:
            start = self._locs[0]

        lat,lon = start.split(',')
        self._lat = lat
        self._lon = lon
        self.get_owner_node().set_position(float(lat),float(lon),self._agl)

        Thread(target=self._publishlocation).start() 
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

    def _publishlocation(self):
        while True:
            loc = self.get_owner_node().get_position()
            uid = self.get_uid()
            message = str(uid) + "," + str(loc[0])  + "," + str(loc[1]) + "," + str(self._agl) + "," + str(self._forward_vel)
            #print "TANKER Publishing: " + message
            m = Message(message, '*')
            self.get_owner_node().get_interface(self._iface_name).send(m,uid)
            time.sleep(0.5)
