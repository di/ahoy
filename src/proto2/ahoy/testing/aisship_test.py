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

n1 = Node(0)
n1.add_interface(Interface('wlan0', wlan, power=120))
#n2 = Node(1)
#n2.add_interface(Interface('wlan0',wlan, power=120))
#n3 = Node(2)
#n3.add_interface(Interface('wlan0',wlan, power=120))


#smalls = SmallShip(n1, 1, 0.0203)
ship1 = AISShip(n1, 0.0203, 12346)
#ship2 = AISShip(n2,0.0300,12346)
#ship3 = AISShip(n3, 0.05,12346)

#n1.add_agent(smalls)
n1.add_agent(ship1)
#n2.add_agent(ship2)
#n3.add_agent(ship3)

n1.set_position(39.881592, -75.172737, 0.02)
#n2.set_position(39.881592, -75.158836, 0.02)
#n3.set_position(39.926441, -75.135262, 0.02)
world.add_entity(n1)
#world.add_entity(n2)
#world.add_entity(n3)


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
