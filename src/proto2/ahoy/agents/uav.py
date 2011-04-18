import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen


class UAV(Agent) :
    def __init__(self, uid, init_lat, init_lon, init_agl, forward_vel, vert_vel) :
        Agent.__init__(self, uid)
        self._lat = init_lat
        self._lon = init_lon
        self._forward_vel = forward_vel
        self._agl = init_agl
        self._vert_vel = vert_vel

    def run(self) :
        uid = self.get_owner_node().get_uid()
        # Set the initial position of the node
        self.get_owner_node().set_position(self._lat,self._lon,self._agl)
        
        #need to call _getnextlocation
        While True:
            time.sleep(1)


    def _move(self, lat, lon, agl, fvel, vvel):
        self.get_owner_node().move(lat, lon, agl, fvel, vvel, True)

    #TODO: Need to add logic for deciding next location
    def _getnextlocation(self):
        return [0,0,0]
