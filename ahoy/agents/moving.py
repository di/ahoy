import random
import time
from ahoy.agent import Agent
from ahoy.message import Message

class MovingAgent(Agent) :
    def __init__(self, owner_node, dest_lat, dest_lon, dest_agl, forward_vel, vert_vel) :
        Agent.__init__(self, owner_node)
        self._dest_lat = dest_lat
        self._dest_lon = dest_lon
        self._dest_agl = dest_agl
        self._forward_vel = forward_vel
        self._vert_vel = vert_vel

    def run(self) :
        o_lat, o_lon, o_agl = self.get_owner_node().get_position()
        self.get_owner_node().move(self._dest_lat, self._dest_lon, self._dest_agl, self._forward_vel, self._vert_vel)
        time.sleep(5)
        print 'moving again'
        self.get_owner_node().move(o_lat, o_lon, o_agl, self._forward_vel, self._vert_vel)
