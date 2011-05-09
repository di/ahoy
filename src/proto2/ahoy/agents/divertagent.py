from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.events.divert import DivertEvent

class DivertAgent(Agent) :
    def __init__(self, uid, interface_name) :
        Agent.__init__(self, uid)
        self._interface_name = interface_name

    def _on_divert(self, event) :
        points = event.get_waypoints()
        message_str = "DIVERT;"
        for i in range(0,len(points)):
            points = points[i]
            message_str += str(points[0]) + "," + str(points[1])
            if( i < len(points) -1):
                message_str += ";"

        message = Message(message_str, "*")
        self.get_owner_node().send(message, self, self.get_owner_node().get_interface(self._interface_name))

    def run(self) :
        self.get_owner_node().get_event_api.subscribe(DivertEvent, self._on_divert)
