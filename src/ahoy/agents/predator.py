from ahoy.agent import Agent
from ahoy.events.predatormessage import PredatorMessage

class PredatorAgent(Agent) :
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(PredatorMessage, self._process_message)
        self.main()

    def main(self) :
        while True :
            pass

    def set_speed(self, velocity, turn_rate) :
        self.get_owner_node().set_speed(velocity * 1/50.0, turn_rate)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PredatorAgent.DEG_PER_SQUARE, cy / PredatorAgent.DEG_PER_SQUARE

    def send_message(self, data) :
        self.get_owner_node().get_event_api().publish(PredatorMessage(self.get_uid(), data))

    def _process_message(self, event) :
        if event.get_src_agent_uid() != self.get_uid() :
            self.on_message_recv(event.get_src_agent_uid(), event.get_contents())

    def on_message_recv(self, src, contents) :
        pass
