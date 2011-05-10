import random
import time
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.units import *

class CommsAgent(Agent) :
    def __init__(self, uid, dest, move) :
        Agent.__init__(self, uid)
        self._dest = dest
        self._move = move

    def on_message(self, event, **kwds) :
        print 'agent %s got message %s' % (self.get_uid(), event.get_message().get_payload())

    def run(self) :
        while True :
            self.get_owner_node().send(Message('this is a test from %s to %s' % (self.get_uid(), self._dest), self._dest), self)
            lat, lon, agl = self.get_owner_node().get_position()
            if self._move :
                self.get_owner_node().set_position(lat + kilometers(.00005), lon, agl)
            else :
                self.get_owner_node().set_position(lat, lon, agl)
            time.sleep(1)
