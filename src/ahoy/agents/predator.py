from ahoy.agent import Agent
from ahoy.events.predatormessage import PredatorMessage

class PredatorAgent(Agent) :
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(PredatorMessage, lambda e: on_message_recv(e.get_contents()))
        self.main()

    def main(self) :
        while True :
            pass

    def move(self, x, y, v) :
        self.get_owner_node().move(PredatorAgent.DEG_PER_SQUARE * y, PredatorAgent.DEG_PER_SQUARE * x, 0, v * 0.00035552, 0, True)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PredatorAgent.DEG_PER_SQUARE, cy / PredatorAgent.DEG_PER_SQUARE

    def send_message(self, data) :
        self.get_owner_node().get_event_api().publish(PredatorMessage(data))

    def on_message_recv(self, contents) :
        pass
