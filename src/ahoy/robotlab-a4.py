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

quads = [ (0, .00444, 0, .00444), (0, -.00444, 0, .00444), (0, .00444, 0, -.00444), (-.00444, 0, -.00444, 0) ]

for q in quads :
    prey = Node(len(world.get_entities()))
    prey.set_position(random.uniform(q[0], q[1]), random.uniform(q[2], q[3]), 0)
    prey.add_agent(PreyAgent(len(world.get_entities())))
    world.add_entity(prey)

    pred = Node(len(world.get_entities()))
    pred.set_position(random.uniform(q[0], q[1]), random.uniform(q[2], q[3]), 0)
    pred.add_agent(PredatorAgentImpl(len(world.get_entities())))
    pred.add_sensor('camera', ForwardCameraSensor(1, 90, 200.0 / 1000.0, use_event_channel=True))
    pred.get_sensor('camera').subscribe(pred.on_camera)
    world.add_entity(pred)

pred = Node(len(world.get_entities()))
pred.add_agent(PredatorAgentImpl(len(world.get_entities())))
pred.add_sensor('camera', ForwardCameraSensor(1, 90, 200.0 / 1000.0, use_event_channel=True))
pred.get_sensor('camera').subscribe(pred.on_camera)
world.add_entity(pred)

if __name__ == '__main__' :
    sim = Simulation(world)

    def quit(signal, frame) :
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
