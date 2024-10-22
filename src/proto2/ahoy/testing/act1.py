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
from ahoy.action import Action
from ahoy.actions.move import MoveAction 
from ahoy.condition import Condition
from ahoy.events.communication import CommunicationSendEvent
from ahoy.agents.divertagent import DivertAgent
from ahoy.conditions.srccondition import SourceCondition
from ahoy.agents.aisship import AISShip
from ahoy.agents.smallship import SmallShip
from ahoy.agents.uav import UAV
from ahoy.agents.sensorforwardagent import SensorForwardAgent
from ahoy.sensors.radarsensor import RadarSensor
from ahoy.sensors.sonarsensor import SonarSensor
from ahoy.agents.correlationagent import CorrelationAgent
from ahoy.util.units import *
from ahoy.sensors.camerasensor import CameraSensor
from ahoy.agents.threat import ThreatShip
from ahoy.agents.tanker import Tanker

path = "agents/paths/path"
pathfile = "agents/paths/tpaths.dat"

world = World()

aisnet = Network('aisn', LogLossComms())
world.add_network(aisnet)
uavnet = Network('uavnet',LogLossComms())
world.add_network(uavnet)

# Make sensor interfaces
s1net = Network('sonar1n', LogLossComms())
world.add_network(s1net)
s2net = Network('sonar2n', LogLossComms())
world.add_network(s2net)
s3net = Network('sonar3n', LogLossComms())
world.add_network(s3net)
r1net = Network('radar1n', LogLossComms())
world.add_network(r1net)

# SW tip of airport
sonar1n = Node(901)
sonar1n.set_position(39.8560599677, -75.255277528, 0)
sonar1n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
sonar1n.add_interface(Interface('sonar1', s1net, power=120))
world.add_entity(sonar1n)

# Eastern bank of river, north of 76 bridge to NJ
sonar2n = Node(len(world.get_entities()))
sonar2n.set_position(39.9103365806, -75.1257383781, 0)
sonar2n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
sonar2n.add_interface(Interface('sonar2', s2net, power=120))
world.add_entity(sonar2n)

# Red Bank Battlefield (nw part of land sticking out south of navy yard)
sonar3n = Node(902)
sonar3n.set_position(39.872596,-75.190008, 0)
sonar3n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=120, use_event_channel=True))
sonar3n.add_interface(Interface('sonar3', s3net, power=120))
world.add_entity(sonar3n)

# On pier of naval yard
radarn = Node(903)
radarn.set_position(39.886597, -75.166043, 0)
radarn.add_sensor('radar', RadarSensor(trans_power=watts(6000), trans_freq=25, gain=1, aperature=5, prop_fact=1, dwell_time=3/360.0, angle=1, use_event_channel=True))
radarn.add_interface(Interface('radar1', r1net, power=12000))
radarn.add_agent(SensorForwardAgent(radarn.get_uid(), 'radar', 'radar1'))
world.add_entity(radarn)

# Ground station
groundst = Node(len(world.get_entities()))
groundst.set_position(39.887911, -75.187533, 0)
groundst.add_interface(Interface('sonar1', s1net, power=12000))
groundst.add_interface(Interface('sonar2', s2net, power=12000))
groundst.add_interface(Interface('radar1', r1net, power=12000))
groundst.add_interface(Interface('aisn', aisnet, power=12000))
groundst.add_interface(Interface('uavnet', uavnet, power=12000))
groundst.add_agent(CorrelationAgent(groundst.get_uid(), 0.5, 0.45, 'aisn'))
#groundst.add_agent(DivertAgent(len(world.get_entities()),'aisn'))
world.add_entity(groundst)

#create tanker
tanknode = Node(len(world.get_entities()))
tanknode.add_interface(Interface('aisn',aisnet,power=120))
tanknode.add_agent(Tanker(tanknode.get_uid(),0.04,'aisn',pathfile))
world.add_entity(tanknode)

# Creat ThreatShip
threatnode = Node(len(world.get_entities()))
tagent = ThreatShip(threatnode.get_uid(),0.07,pathfile)
tagent.follow(tanknode.get_uid())
threatnode.add_agent(tagent)
world.add_entity(threatnode)

#Create UAV at airport
uavnode = Node(len(world.get_entities()))
uavnode.set_position(39.8661,-75.2549, 0.0001)
uavnode.add_interface(Interface('uavnet',uavnet,power=120))
uavnode.add_sensor('camera', CameraSensor(1.75,0.25,use_event_channel=True))
uavnode.add_agent(SensorForwardAgent(uavnode.get_uid(),'camera','uavnet'))
uavnode.add_agent(UAV(8,1.0,0.10,0.025))
world.add_entity(uavnode)

#Small personal craft
for i in range(0,9):
    n = Node(len(world.get_entities()))
    ship = SmallShip(n.get_uid(), i, 0.03, path + str(i) + ".dat")
    n.add_agent(ship)
    world.add_entity(n)

#AIS Ships
for i in range(0, 16):
	n = Node(len(world.get_entities()))
	n.add_interface(Interface('aisn', aisnet, power=120))
	ship = AISShip(n.get_uid(), 0.03, 'localhost', 12348, 'aisn')
	n.add_agent(ship)
	world.add_entity(n)

if __name__ == '__main__' :
    sim = Simulation(world)

    def quit(signal, frame) :
        print 'Stopping...'
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(5)

    while True :
        pass
