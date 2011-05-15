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
from ahoy.sensors.chemicalsensor import ChemicalSensor
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.agents.chemspillannounce import ChemicalSpillAnnounceAgent

path = "agents/paths/path"
pathfile = "agents/paths/tpaths2.dat"

world = World()

aisnet = Network('aisn', LogLossComms())
world.add_network(aisnet)
'''
# Red Bank Battlefield (nw part of land sticking out south of navy yard)
sonar3n = Node(902)
sonar3n.set_position(39.872596,-75.190008, 0)
sonar3n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=120, use_event_channel=True))
world.add_entity(sonar3n)

# On pier of naval yard
radarn = Node(903)
radarn.set_position(39.886597, -75.166043, 0)
radarn.add_sensor('radar', RadarSensor(trans_power=watts(6000), trans_freq=25, gain=1, aperature=5, prop_fact=1, dwell_time=3/360.0, angle=1, use_event_channel=True))
radarn.add_agent(SensorForwardAgent(radarn.get_uid(), 'radar', 'radar1'))
world.add_entity(radarn)
'''
# Ground station
groundst = Node(len(world.get_entities()))
groundst.set_position(39.887911, -75.187533, 0)
groundst.add_interface(Interface('aisn', aisnet, power=12000))
groundst.add_agent(DivertAgent(len(world.get_entities()),'aisn'))
world.add_entity(groundst)

#create tanker
tanknode = Node(len(world.get_entities()))
tanknode.add_interface(Interface('aisn',aisnet,power=120))
tanknode.add_agent(Tanker(80,0.08,'aisn',pathfile))
world.add_entity(tanknode)

active = [[39.890750000000004, -75.196423312500002], [39.883578125, -75.195800625000004], [39.878743749999998, -75.196907624999994], [39.873325000000001, -75.202165874999992], [39.869075000000002, -75.208600312499996], [39.8930875, -75.193794187500004], [39.888784375, -75.193725000000001], [39.886287500000002, -75.196215749999993], [39.885490625000003, -75.193309874999997], [39.882303125, -75.192272062499995], [39.881718750000005, -75.198222187499994], [39.880125, -75.201612374999996], [39.877787500000004, -75.204725812500001], [39.875450000000001, -75.207008999999999], [39.872740624999999, -75.211437000000004], [39.876512500000004, -75.201681562499999], [39.869871875000001, -75.204379875000001], [39.86981875, -75.214204499999994], [39.875396875, -75.197599499999995], [39.879062500000003, -75.191856937499992], [39.867587499999999, -75.220292999999998], [39.866631250000005, -75.215934187499997], [39.863975000000003, -75.213581812499996], [39.863709374999999, -75.219808687499992], [39.864931249999998, -75.226589062499997], [39.892609374999999, -75.201197249999993], [39.894893750000001, -75.203480437500005], [39.894309374999999, -75.207285749999997], [39.896646875000002, -75.208600312499996], [39.898293750000001, -75.213305062499998], [39.900950000000002, -75.212889937499995], [39.872475000000001, -75.207147374999991], [39.870350000000002, -75.199744312500002], [39.875450000000001, -75.193863374999992], [39.872262500000005, -75.196077375000002], [39.861637500000001, -75.218632499999998], [39.861212500000001, -75.226727437500003], [39.862275000000004, -75.232262437499998]]

for loc in active :
#for i in range(0,len(active),2) :
#    loc = active[i]
    chem = Node(len(world.get_entities()))
    chem.add_sensor('chemical', ChemicalSensor(interval=1, use_event_channel='hey aaron i think this is broken'))
    chem.set_position(loc[0], loc[1], 0)
    world.add_entity(chem)

inactive = [[39.857068750000003, -75.224790187499991], [39.857387500000002, -75.217594687499997], [39.860468750000003, -75.213235874999995], [39.863921875000003, -75.206178749999992], [39.866790625, -75.209914874999996], [39.866418750000001, -75.202304249999997], [39.869659375000005, -75.197115187500003], [39.865834374999999, -75.195731437500001], [39.869978125000003, -75.192064500000001], [39.874546875, -75.188328374999998], [39.876193749999999, -75.183762000000002], [39.877043749999999, -75.190127250000003], [39.879646874999999, -75.186944624999995], [39.882621874999998, -75.188051625], [39.885278124999999, -75.186321937499997], [39.885278124999999, -75.182793375000003], [39.885596875000005, -75.178088625000001], [39.882674999999999, -75.183346874999998], [39.880284375000002, -75.182378249999999], [39.877787500000004, -75.179956687499995], [39.879168749999998, -75.175943812499995], [39.881240625000004, -75.178434562500001], [39.883259375000002, -75.178642124999996], [39.879168749999998, -75.171654187499996], [39.883206250000001, -75.173037937499998], [39.88618125, -75.172553624999992], [39.882834375000002, -75.168402374999999], [39.885862500000002, -75.1670878125], [39.879009375000003, -75.165496500000003], [39.88660625, -75.161552812500005], [39.883365625000003, -75.162867375000005], [39.878690625000004, -75.160999312499996], [39.881240625000004, -75.158646937499995], [39.885012500000002, -75.156848062500003], [39.878425, -75.155118375000001], [39.881718750000005, -75.154218937500005], [39.887137500000001, -75.153250312499992], [39.884693750000004, -75.150552000000005], [39.880390625000004, -75.149929312499992], [39.878690625000004, -75.146400749999998], [39.882621874999998, -75.145570500000005], [39.887509375, -75.146885062500004]]

#for i in range(0,len(inactive),2) :
#    loc = inactive[i]
for loc in inactive :
    chem = Node(len(world.get_entities()))
    chem.add_sensor('chemical', ChemicalSensor(interval=9000))
    chem.set_position(loc[0], loc[1], 0)
    world.add_entity(chem)

chemspill = Node(len(world.get_entities()))
chemspill.set_position(39.892223,-75.196788, 0) #immediately east of I-95 bridge, on water
chemspill.add_agent( ChemicalSpillAnnounceAgent(2, 1, 20, 0.05) )   #ID, interval, announce time, spill rate in km/s
world.add_entity(chemspill)

#AIS Ships
for i in range(0, 16):
	n = Node(len(world.get_entities()))
	n.add_interface(Interface('aisn', aisnet, power=120))
	ship = AISShip(n.get_uid(), 0.0203, 'localhost', 12348, 'aisn')
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
