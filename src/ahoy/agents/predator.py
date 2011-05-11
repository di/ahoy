from ahoy.agent import Agent
from ahoy.events.predatormessage import PredatorMessage
from ahoy.events.preymessage import PreyMessage

class PredatorAgent(Agent) :
    DEG_PER_SQUARE = .004444 / 25.0
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def run(self) :
        self.get_owner_node().get_event_api().subscribe(PredatorMessage, self._process_predator_message)
        self.get_owner_node().get_event_api().subscribe(PreyMessage, self._process_prey_message)
        self.get_owner_node().get_sensor('camera').subscribe(self._process_camera)
        self.main()

    def main(self) :
        while True :
            pass

    def set_speed(self, velocity, turn_rate) :
#        velocity = min(velocity, 2 * PredatorAgent.DEG_PER_SQUARE)
        velocity = min(velocity * 1/50.0, 2.0 / 50.0)
        self.get_owner_node().set_speed(velocity, turn_rate)

    def get_position(self) :
        cx, cy, cz = self.get_owner_node().get_position()
        return cx / PredatorAgent.DEG_PER_SQUARE, cy / PredatorAgent.DEG_PER_SQUARE

    def get_rotation(self) :
        return self.get_owner_node().get_bearing()

    def send_message(self, data) :
        self.get_owner_node().get_event_api().publish(PredatorMessage(self.get_uid(), data))

    def _process_predator_message(self, event) :
        if event.get_src_agent_uid() != self.get_uid() :
            self.on_message_recv(event.get_src_agent_uid(), event.get_contents())

    def _process_prey_message(self, event) :
        if not event.is_alive() :
            self.on_prey_death(event.get_pos(), event.get_src_agent_uid())

    def _process_camera(self, event) :
        if len(event.get_visible()) > 0 :
            locs = []
            for v in event.get_visible() :
                x = v[0] / PredatorAgent.DEG_PER_SQUARE
                y = v[1] / PredatorAgent.DEG_PER_SQUARE
                locs.append((x, y))
            self.on_camera(locs)

    def on_message_recv(self, src, contents) :
        pass

    def on_prey_death(self, pos, uid) :
        pass

    def on_camera(self, locs) :
        pass
