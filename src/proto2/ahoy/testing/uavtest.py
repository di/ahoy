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

world = World()
wlan = Network('wlan0', LogLossComms())
uavnet = Network('uavnet',LogLossComms())

world.add_network(wlan)
world.add_network(uavnet)
path = "agents/paths/path"
pathfile = "agents/paths/tpaths.dat"

uavnode = Node(1)
uavnode.set_position(39.8661,-75.2549, 0.0001)
#uavnode.set_position(39.8656978,-75.21841399, 0.0001)
uavnode.add_interface(Interface('uavnet',uavnet,power=120))
uavnode.add_sensor('camera', CameraSensor(1.75,0.25,use_event_channel=True))
uavnode.add_agent(SensorForwardAgent(uavnode.get_uid(),'camera','uavnet'))
uavnode.add_agent(UAV(8,1.0,0.045,0.015))


world.add_entity(uavnode)

"""
for i in range(5,15):
	n = Node(i)
	n.add_interface(Interface('wlan0',wlan, power=120))
	ship = AISShip((i + 51),0.0203,12346, 'wlan0')
	n.add_agent(ship)
	world.add_entity(n)
"""

for i in range(0,9):
    n = Node(i+100)
    ship = SmallShip(i+200, i, 0.02, path + str(i) + ".dat")
    n.add_agent(ship)
    world.add_entity(n)

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
