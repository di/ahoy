import sys
from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node

world = World()
world.add_entity(Node(0))

Simulation(world).start(2)
