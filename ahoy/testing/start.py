import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.commsengines.basic import BasicComms
from ahoy.commsengines.logloss import LogLossComms
from ahoy.interface import Interface
from ahoy.agents.comms import CommsAgent
from ahoy.network import Network
from ahoy.tcpforward import TcpForward

world = World()
wlan = Network('wlan0')
world.add_network(wlan)

n1 = Node(0)
n1.add_interface(Interface('wlan0', n1, wlan, 100))
n1.add_agent(CommsAgent(n1, 'wlan0', 1, False))
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)

n2 = Node(1)
n2.add_interface(Interface('wlan0', n2, wlan, 100))
n2.add_agent(CommsAgent(n2, 'wlan0', 0, True))
n2.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n2)

if __name__ == '__main__' :
    sim = Simulation(world, LogLossComms())

    def quit(signal, frame) :
        print 'Stopping...'
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
