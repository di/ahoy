#This file is used solely to test the way behaviors act
# for agents


import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.commsengines.basic import BasicComms
from ahoy.commsengines.logloss import LogLossComms
from ahoy.interface import Interface
from ahoy.agents.comms import CommsAgent
from ahoy.agents.tstcomms import TstCommsAgent
from ahoy.network import Network
from ahoy.tcpforward import TcpForward
from ahoy.action import Action
from ahoy.condition import Condition

world = World()
wlan = Network('wlan0')
world.add_network(wlan)

n1 = Node(0)
n1.add_interface(Interface('wlan0', n1, wlan, 100))

ca1 = TstCommsAgent(n1, 'wlan0', 1, False)
act = Action('testaction')
con = Condition('testcondition','test')
ca1.add_behavior([con,'CommunicationSendEvent',act])

n1.add_agent(ca1)
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)

n2 = Node(1)
n2.add_interface(Interface('wlan0', n2, wlan, 100))

ca2 = TstCommsAgent(n2, 'wlan0', 0, True)
act2 = Action('testaction')
con2 = Condition('testcondition','test')
ca2.add_behavior([con2,'CommunicationSendEvent',act2])

n2.add_agent(ca2)
n2.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n2)

if __name__ == '__main__' :
    sim = Simulation(world, LogLossComms(), TcpForward(int(sys.argv[1])))

    def quit(signal, frame) :
        print 'Stopping...'
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
