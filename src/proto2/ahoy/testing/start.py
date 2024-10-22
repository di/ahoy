import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.commsengines.logloss import LogLossComms
from ahoy.interface import Interface
from ahoy.agents.comms import CommsAgent
from ahoy.network import Network
from ahoy.tcpforward import TcpForward

world = World()
wlan = Network('wlan0', LogLossComms())
world.add_network(wlan)

n1 = Node(0)
n1.add_interface(Interface('wlan0', wlan, power=100))
n1.add_agent(CommsAgent(5, 6, False))
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)

n2 = Node(1)
n2.add_interface(Interface('wlan0', wlan, power=100))
n2.add_agent(CommsAgent(6, 7, False))
n2.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n2)

n3 = Node(2)
n3.add_interface(Interface('wlan0', wlan, power=100))
n3.add_agent(CommsAgent(7, 5, False))
n3.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n3)

if __name__ == '__main__' :
    sim = Simulation(world)

    def quit(signal, frame) :
        print 'Stopping...'
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
