from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node
from stage.network import Network
from stage.interface import Interface

world = World()
#wlan = Network('wlan0')
for i in range(0, 4) :
    n = Node(i)
    #n.add_interface('wlan0', Interface(n, wlan))
    world.add_entity(n)

Simulation(world).start(2)
