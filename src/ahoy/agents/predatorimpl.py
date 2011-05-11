import time
import math
from ahoy.agents.predator import PredatorAgent

class PredatorAgentImpl(PredatorAgent) :
    def __init__(self, uid) :
        PredatorAgent.__init__(self, uid)
        '''
        Add any additional constructor code here
        '''

    '''
    Main method which is called at startup 
    For this example, the robot simply weaves back and forth
    '''
    def main(self) :
        rotation = math.radians(50)
        while True :
            '''
            set_speed(blocks_per_second, radians_per_second)

            NOTE: The max for this is 2 blocks/sec.
            '''
            self.set_speed(1, rotation)
            rotation *= -1
            x, y = self.get_position()
            '''
            Example communication: Sends a string message to all other predators with the new location.
            The contents being sent can be any serializable object, not just a string.
            '''
            self.send_message('new_loc %s %s' % (x, y))

            time.sleep(2)

    '''
    This method is automatically invoked when a message from another predator is received.
    '''
    def on_message_recv(self, src, contents) :
        print 'Predator %s got message "%s" from predator %s' % (self.get_uid(), contents, src)

    '''
    This method is automatically invoked when a prey dies.
    '''
    def on_prey_death(self, pos, uid) :
        x, y = pos
        print 'Predator %s heard that prey %s at %s, %s died' % (self.get_uid(), uid, x, y)
