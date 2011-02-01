from ahoy.condition import Condition
from ahoy.agent import Agent
from ahoy.entity import Entity
from ahoy.events.communication import CommunicationSendEvent
from ahoy.events.communication import CommunicationRecvEvent
from ahoy.events.move import EntityMoveEvent

class SourceCondition(Condition):

    def __init__(self,entity_uid):
        Condition.__init__(self)        
        self._entity_uid = entity_uid

    #check the type of the event. Then see if the uid matches
    def is_met(self, event):
        if (event.__class__ == CommunicationSendEvent):
            if(event.get_src_agent_uid() == self._entity_uid):
                print "Returning true of CommSendEvent"
                return True
        elif(event.__class__ == EntityMoveEvent):
            if(event.get_uid() == self._entity_uid):
                print "Returning true of Move Event"
                return True
        print "Condition is false"
        return False
