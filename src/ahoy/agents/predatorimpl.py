from ahoy.agents.predator import PredatorAgent

class PredatorAgentImpl(PredatorAgent) :
    def __init__(self, uid) :
        PredatorAgent.__init__(self, uid)
        ''' Add any additional constructor code here '''

    def main(self) :
        ''' Main method which is called at startup '''
        print 'start', self.get_position()
        self.move(1, 0, 10)
        print 'end', self.get_position()
