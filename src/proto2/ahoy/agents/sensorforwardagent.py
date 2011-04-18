from ahoy.agent import Agent
from ahoy.message import Message

class SensorForwardAgent(Agent) :
    def __init__(self, uid, sensor_name, interface_name, dest_agent='*') :
        Agent.__init__(self, uid)
        self._sensor_name = sensor_name
        self._interface_name = interface_name
        self._dest_agent = dest_agent

    def _on_sensor(self, event) :
        message = Message(event.__str__(), self._dest_agent)
        self.get_owner_node().send(message, self, self.get_owner_node().get_interface(self._interface_name))

    def run(self) :
        self.get_owner_node().get_sensor(self._sensor_name).subscribe(self._on_sensor)
