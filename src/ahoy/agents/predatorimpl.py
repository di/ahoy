import math
from ahoy.agents.predator import PredatorAgent

class PredatorAgentImpl(PredatorAgent) :
    def __init__(self, uid) :
        PredatorAgent.__init__(self, uid)
        ''' Add any additional constructor code here '''

    def main(self) :
        ''' Main method which is called at startup '''
        self.set_speed(1, math.radians(20))
