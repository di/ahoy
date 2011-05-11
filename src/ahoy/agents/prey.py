import random, time, math
from ahoy.agent import Agent
from ahoy.events.preymessage import PreyMessage

class PreyAgent(Agent) :
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)
        self._alive = True

    def run(self) :
        self.main()

    def main(self) :
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
            t = WAIT_SEC+ random.random() * WAIT_JIT
            time.sleep(t)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PreyAgent.DEG_PER_SQUARE, cy / PreyAgent.DEG_PER_SQUARE

    def die(self) :
        self._alive = False
        self.get_owner_node().get_event_api().publish(PreyMessage(self.get_uid(), self._alive))
        print 'Prey "', self.get_uid(), '" has been killed!"'
