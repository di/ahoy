from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node

world = World()
for i in range(0, 4) :
    world.add_entity(Node(i))

Simulation(world).start(2)
