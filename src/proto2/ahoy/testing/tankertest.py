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
from ahoy.agents.uav import UAV
from ahoy.agents.smallship import SmallShip
from ahoy.sensors.radarsensor import RadarSensor
from ahoy.sensors.sonarsensor import SonarSensor
from ahoy.sensors.camerasensor import CameraSensor
from ahoy.util.units import *
from ahoy.agents.sensorforwardagent import SensorForwardAgent
from ahoy.sensors.camerasensor import CameraSensor
from ahoy.agents.threat import ThreatShip
from ahoy.agents.tanker import Tanker
from ahoy.agents.correlationagent import CorrelationAgent

world = World()
wlan = Network('wlan0', LogLossComms())
tnet = Network('tnet',LogLossComms())

world.add_network(wlan)
world.add_network(tnet)

path = "agents/paths/path"
pathfile = "agents/paths/tpaths.dat"

tanknode = Node(len(world.get_entities()))
#uavnode.set_position(39.8656978,-75.21841399, 0.0001)
tanknode.add_interface(Interface('tnet',tnet,power=120))
tanknode.add_agent(Tanker(80,0.08,'tnet',pathfile))
world.add_entity(tanknode)

threatnode = Node(len(world.get_entities()))
tagent = ThreatShip(81,0.10,pathfile)
tagent.follow(tanknode.get_uid())
threatnode.add_agent(tagent)
world.add_entity(threatnode)

#for i in range(0,4):
#    n = Node(i+100)
#    ship = SmallShip(i+200, i, 0.03, path + str(i) + ".dat")
#    n.add_agent(ship)
#    world.add_entity(n)
 

# Make sensor interfaces
s1net = Network('sonar1n', LogLossComms())
world.add_network(s1net)
s2net = Network('sonar2n', LogLossComms())
world.add_network(s2net)
s3net = Network('sonar3n', LogLossComms())
world.add_network(s3net)
r1net = Network('radar1n', LogLossComms())
world.add_network(r1net)
'''
# SW tip of airport
sonar1n = Node(901)
sonar1n.set_position(39.8560599677, -75.255277528, 0)
sonar1n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=120, use_event_channel=True))
sonar1n.add_interface(Interface('sonar1', s1net, power=120))
sonar1n.add_agent(SensorForwardAgent(sonar1n.get_uid(), 'sonar', 'sonar1'))
world.add_entity(sonar1n)

# Eastern bank of river, north of 76 bridge to NJ
sonar2n = Node(len(world.get_entities()))
sonar2n.set_position(39.9103365806, -75.1257383781, 0)
sonar2n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=120, use_event_channel=True))
sonar2n.add_interface(Interface('sonar2', s2net, power=120))
sonar2n.add_agent(SensorForwardAgent(sonar2n.get_uid(), 'sonar', 'sonar2'))
world.add_entity(sonar2n)
'''

# Red Bank Battlefield (nw part of land sticking out south of navy yard)
sonar3n = Node(902)
sonar3n.set_position(39.875131,-75.193532, 0)
sonar3n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=120, use_event_channel=True))
sonar3n.add_interface(Interface('sonar3', s3net, power=120))
#sonar3n.add_agent(SensorForwardAgent(sonar3n.get_uid(), 'sonar', 'sonar3'))
world.add_entity(sonar3n)



# On pier of naval yard
radarn = Node(len(world.get_entities()))
radarn.set_position(39.886597, -75.166043, 0)
radarn.add_sensor('radar', RadarSensor(trans_power=watts(6000), trans_freq=25, gain=1, aperature=5, prop_fact=1, dwell_time=3/360.0, angle=1, use_event_channel=True))
radarn.add_interface(Interface('radar1', r1net, power=12000))
#radarn.add_agent(SensorForwardAgent(radarn.get_uid(), 'radar', 'radar1'))
world.add_entity(radarn)

# Ground station
groundst = Node(len(world.get_entities()))
groundst.set_position(39.887911, -75.187533, 0)
#groundst.add_interface(Interface('sonar1', s1net, power=12000))
#groundst.add_interface(Interface('sonar3', s3net, power=12000))
#groundst.add_interface(Interface('radar1', r1net, power=12000))
groundst.add_interface(Interface('tnet', tnet, power=12000))
groundst.add_agent(CorrelationAgent(groundst.get_uid(), 0.6, 0.03, 'sonar1', 'sonar3', 'radar1', 'tnet'))
#groundst.add_agent(HistoryCorrelationAgent(groundst.get_uid(), 0.1, 0.001, 'sonar1', 'sonar2', 'radar1', 'ais1', 4, 0.05, 0.5))
#groundst.add_agent(DivertAgent(len(world.get_entities()),'ais1'))
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
