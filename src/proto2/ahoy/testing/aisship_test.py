#This file is used solely to test the way behaviors act
# for agents


import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
#from ahoy.commsengines.basic import BasicComms
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
from ahoy.agents.aisship import AISShip
from ahoy.agents.smallship import SmallShip

world = World()
wlan = Network('wlan0', LogLossComms())
world.add_network(wlan)


for i in range(0,2):
	n = Node(i)
	n.add_interface(Interface('wlan0',wlan, power=120))
	ship = AISShip(n,0.0203,12346)
	n.add_agent(ship)
	world.add_entity(n)

'''
n1 = Node(0)
n1.add_interface(Interface('wlan0',wlan,power=120))
ship = AISShip(n1,0.023,12346)
n1.add_agent(ship)
world.add_entity(n1)
'''

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
