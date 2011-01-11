import sys
import signal
from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node
from stage.commsengines.basic import BasicComms
from stage.interface import Interface
from stage.agents.comms import CommsAgent
from stage.network import Network
from stage.tcpforward import TcpForward

world = World()
wlan = Network('wlan0')
world.add_network(wlan)

n1 = Node(0)
n1.add_interface('wlan0', Interface(n1, wlan))
n1.add_agent(CommsAgent(n1, 'wlan0', 1, False))
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)
n2 = Node(1)
n2.add_interface('wlan0', Interface(n2, wlan))
n2.add_agent(CommsAgent(n2, 'wlan0', 0, True))
n2.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n2)
'''
for i in range(0, 4) :
    n = Node(i)
    n.add_interface('wlan0', Interface(n, wlan))
    n.add_agent(CommsAgent(n, 'wlan0', (i+1) % 4))
    world.add_entity(n)
'''

if __name__ == '__main__' :
    def quit(signal, frame) :
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    Simulation(world, BasicComms(), TcpForward(int(sys.argv[1]))).start(2)
