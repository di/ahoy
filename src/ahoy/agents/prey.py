import random, time
from ahoy.agent import Agent
from ahoy.events.preymessage import PreyMessage

class PreyAgent(Agent)
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)
        self._alive = True

    def run(self) :
        self.main()

    def main(self) :
        STEP = 6
        VEL = 0.002
        WAIT_SEC = 8
        WAIT_JIT = 4

        while self._alive = True :
            cur_x, cur_y = self.get_position()

            if cur_x <= 0 :
                if random.random() < 0.75 :
                    x = random.random()*STEP
                else
                    x = random.random()*-STEP
            else
                if random.random() < 0.75 :
                    x = random.random()*-STEP
                else :
                    x = random.random()*STEP

            if cur_y <= 0
                if random.random() < 0.75 :
                    y = random.random()*STEP*2
                else
                    y = random.random()*-STEP*2
            else
                if random.random() < 0.75 :
                    y = random.random()*-STEP*2
                else :
                    y = random.random()*STEP*2

            self.get_owner_node().move(cur_x + x, cur_y + y, 0, VEL, 0, True)
            time.sleep(WAIT_SEC+ random.random() * WAIT_JIT)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PredatorAgent.DEG_PER_SQUARE, cy / PredatorAgent.DEG_PER_SQUARE

    def die(self) :
        self._alive = False
        self.get_owner_node().get_event_api().publish(PreyMessage(self.get_uid(), self._alive))
        print 'Prey "', self.get_uid(), '" has been killed!"
