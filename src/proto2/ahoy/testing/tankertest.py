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

world = World()
wlan = Network('wlan0', LogLossComms())
tnet = Network('tnet',LogLossComms())

world.add_network(wlan)
world.add_network(tnet)

pathfile = "agents/paths/tpaths.dat"

tanknode = Node(1)
#uavnode.set_position(39.8656978,-75.21841399, 0.0001)
tanknode.add_interface(Interface('tnet',tnet,power=120))
tanknode.add_agent(Tanker(80,0.08,'tnet',pathfile))

threatnode = Node(2)
tagent = ThreatShip(81,0.10,pathfile)
tagent.follow(1)
threatnode.add_agent(tagent)

world.add_entity(tanknode)
world.add_entity(threatnode)


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
