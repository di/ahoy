import random
import time
import math
from ahoy.util.geo import *
from ahoy.agent import Agent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.preymessage import PreyMessage

class PreyAgent(Agent) :
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)
        self._alive = True
        self._sides = { 0 : None, 90 : None, 180 : None, 270 : None }

    def _on_move(self, event) :
        agents = self.get_owner_node().get_world().get_entity(event.get_uid()).get_agents().values()
        if 'PredatorAgentImpl' in map(lambda a : a.__class__.__name__, agents) :
            x, y = self.get_position()
            pred_x, pred_y = event.get_lat() / PreyAgent.DEG_PER_SQUARE, event.get_long() / PreyAgent.DEG_PER_SQUARE
            dist = math.sqrt((pred_x - x)**2 + (pred_y - y)**2)
            if dist < 3.0 :
                lat1, lon1, _ = self.get_owner_node().get_position()
                lat2, lon2 = event.get_lat(), event.get_lon()
                angle = bearing_from_points(lat1, lon1, lat2, lon2)
                print '>', event.get_uid(), 'in range', angle

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(EntityMoveEvent, self._on_move)
        STEP = 6
        VEL = 0.010
        WAIT_SEC = 1
        WAIT_JIT = 1
        MAX = 25
        BUFFER = 1

        while self._alive == True :
            cur_x, cur_y = self.get_position()
            self.get_owner_node().set_speed(VEL, math.radians(random.uniform(-20, 20)))

            if cur_x >= MAX - BUFFER or cur_x <= -MAX + BUFFER or cur_y >= MAX - BUFFER or cur_y <= -MAX + BUFFER :
                self.get_owner_node().set_bearing(math.radians(self.get_owner_node().get_bearing() + 180))
                self.get_owner_node().set_speed(VEL, 0)
            t = WAIT_SEC + random.random() * WAIT_JIT
            time.sleep(t)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PreyAgent.DEG_PER_SQUARE, cy / PreyAgent.DEG_PER_SQUARE

    def die(self) :
        self._alive = False
        self.get_owner_node().get_event_api().publish(PreyMessage(self.get_uid(), self.get_position(), self._alive))
        print 'Prey %s at %s has been killed!' % (self.get_uid(), self.get_position())
