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
for i in range(0, 4) :
    n = Node(i)
    n.add_interface('wlan0', Interface(n, wlan))
    n.add_agent(CommsAgent(n, 'wlan0', (i+1) % 4))
    world.add_entity(n)

if __name__ == '__main__' :
    def quit(signal, frame) :
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    Simulation(world, BasicComms(), TcpForward(int(sys.argv[1]))).start(2)
