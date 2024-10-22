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
from ahoy.network import Network
from ahoy.tcpforward import TcpForward
from ahoy.action import Action
from ahoy.actions.move import MoveAction 
from ahoy.condition import Condition
from ahoy.events.communication import CommunicationSendEvent
from ahoy.conditions.srccondition import SourceCondition

world = World()
wlan = Network('wlan0')
world.add_network(wlan)

n1 = Node(0)
n1.add_interface(Interface('wlan0', n1, wlan, 100))

ca1 = CommsAgent(n1, 1, 2, False)
n1.add_agent(ca1)
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)

n2 = Node(1)
n2.add_interface(Interface('wlan0', n2, wlan, 100))

ca2 = CommsAgent(n2, 2, 1, True)

n2.add_agent(ca2)
n2.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n2)

act = MoveAction(n1,1,1,0)
con = SourceCondition(2)
ca1.add_behavior([con,CommunicationSendEvent,act])

act2 = MoveAction(n2,-1,-1,2)
con2 = SourceCondition(1)
ca2.add_behavior([con2,CommunicationSendEvent,act2])

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
