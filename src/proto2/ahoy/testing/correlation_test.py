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
from ahoy.sensors.radarsensor import RadarSensor
from ahoy.sensors.sonarsensor import SonarSensor
from ahoy.util.units import *

world = World()
aisnet = Network('aisn', LogLossComms())
world.add_network(wlan)


for i in range(0,2):
	n = Node(i)
	n.add_interface(Interface('ais1', aisnet, power=120))
	ship = AISShip((i + 21),0.0203,12346, 'ais1')
	n.add_agent(ship)
	world.add_entity(n)

# Make sensor interfaces
s1net = Network('sonar1n', LogLossComms())
world.add_network(s1net)
s2net = Network('sonar2n', LogLossComms())
world.add_network(s2net)
r1net = Network('radar1n', LogLossComms())
world.add_network(r1net)

# SW tip of airport
sonar1n = Node(len(world.get_entities()))
sonar1n.set_position(39.8560599677, -75.255277528, 0)
sonar1n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
sonar1n.add_interface(Interface('sonar1', s1net, power=120))
world.add_entity(sonar1n)

# Eastern bank of river, north of 76 bridge to NJ
sonar2n = Node(len(world.get_entities()))
sonar2n.set_position(39.9103365806, -75.1257383781, 0)
sonar2n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
groundst.add_interface(Interface('sonar2', s2net, power=120))
world.add_entity(sonar2n)

# On pier of naval yard
radarn = Node(len(world.get_entities()))
radarn.set_position(39.886597, -75.166043, 0)
radarn.add_sensor('radar', RadarSensor(trans_power=watts(6000), trans_freq=25, gain=1, aperature=5, prop_fact=1, dwell_time=3/360.0, angle=1))
groundst.add_interface(Interface('radar1', r1net, power=120))
world.add_entity(radarn)


# Ground station
groundst = Node(len(world.get_entities()))
groundst.add_interface(Interface('sonar1', s1net, power=120))
groundst.add_interface(Interface('sonar2', s2net, power=120))
groundst.add_interface(Interface('radar1', r1net, power=120))

groundst.add_agent( CorrelationAgent( groundst.get_uid(), threat_dist=0.01, 'sonar1', 'sonar2', 'radar1', 'ais1') )



world.add_entity(groundst)

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