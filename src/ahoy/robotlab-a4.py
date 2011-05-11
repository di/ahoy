import signal
import sys
import random
from ahoy.world import World
from ahoy.simulation import Simulation
from ahoy.entities.node import Node
from ahoy.sensors.forwardcamera import ForwardCameraSensor
from ahoy.agents.predatorimpl import PredatorAgentImpl
from ahoy.agents.prey import PreyAgent

world = World()
for pred_id in range(0, 5) :
    pred = Node(len(world.get_entities()))
    pred.add_agent(PredatorAgentImpl(len(world.get_entities())))
    pred.add_sensor('camera', ForwardCameraSensor(1, 90, 200.0 / 1000.0, use_event_channel=True))
    world.add_entity(pred)

# T/R
prey = Node(len(world.get_entities()))
prey.add_agent(PreyAgent(len(world.get_entities())))
prey.set_position(random.uniform(0, .00444), random.uniform(0, .00444), 0)
world.add_entity(prey)

# T/L
prey = Node(len(world.get_entities()))
prey.add_agent(PreyAgent(len(world.get_entities())))
prey.set_position(random.uniform(0, -.00444), random.uniform(0, .00444), 0)
world.add_entity(prey)

# B/R
prey = Node(len(world.get_entities()))
prey.add_agent(PreyAgent(len(world.get_entities())))
prey.set_position(random.uniform(0, .00444), random.uniform(0, -.00444), 0)
world.add_entity(prey)

# B/L
prey = Node(len(world.get_entities()))
prey.add_agent(PreyAgent(len(world.get_entities())))
prey.set_position(random.uniform(-.00444, 0), random.uniform(-.00444, 0), 0)
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
