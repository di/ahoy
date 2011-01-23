# This class used solely to test the behaviors of
# agents on events

import random
import time
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.units import *

class TstCommsAgent(Agent) :
    def __init__(self, owner_node, iface_name, dests, move) :
        Agent.__init__(self, owner_node)
        self._iface_name = iface_name
        self._dests = dests
        self._move = move

    def _on_message(self, event, **kwds) :
        print 'got the message'    

    def run(self) :
        iface = self.get_owner_node().get_interface(self._iface_name)
        iface.set_recv_callback(self._on_message)
        while True :
            iface.send(Message('this is a test from %s to %s' % (self.get_owner_node().get_uid(), self._dests), self._dests))
            lat, lon, agl = self.get_owner_node().get_position()
            if self._move :
                self.get_owner_node().set_position(lat + kilometers(.00005), lon, agl)
            else :
                self.get_owner_node().set_position(lat, lon, agl)
            time.sleep(1)
