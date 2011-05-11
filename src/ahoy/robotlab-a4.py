import signal
import sys
from ahoy.world import World
from ahoy.simulation import Simulation
from ahoy.entities.node import Node
from ahoy.sensors.forwardcamera import ForwardCameraSensor
from ahoy.agents.predatorimpl import PredatorAgentImpl

world = World()

for pred_id in range(0, 5) :
    pred = Node(pred_id)
    pred.add_agent(PredatorAgentImpl(pred_id))
    pred.add_sensor('camera', ForwardCameraSensor(0, 60, use_event_channel=True))
    world.add_entity(pred)

for prey_id in range(5, 9) :
    prey = Node(prey_id)
    prey.add_agent(PreyAgent(prey_id))
    world.add_entity(prey)

if __name__ == '__main__' :
    sim = Simulation(world)

    def quit(signal, frame) :
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
