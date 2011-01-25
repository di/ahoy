import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.entities.radarsensor2 import RadarSensor2
from ahoy.entities.scripted import Scripted
from ahoy.agents.rectanglesurveil import RectangleSurveilAgent
from ahoy.commsengines.logloss import LogLossComms
from ahoy.tcpforward import TcpForward
from ahoy.network import Network
from ahoy.interface import Interface
from ahoy.util.units import *

world = World()

wlan = Network('wlan0')
world.add_network(wlan)

heli_areas = [(39.9558, -75.1386, 39.9475, -75.1314), (39.9468, -75.1396, 39.9419, -75.1314), (39.9410, -75.1420, 39.9360, -75.1321), (39.9330, -75.1418, 39.9281, -75.1311)]
for i, loc in enumerate(heli_areas) :
    print 'heli', i
    heli = Node(i)
    heli.set_position(loc[0], loc[1], feet(i * 100))
    nw = (loc[0], loc[1])
    se = (loc[2], loc[3])
    heli.add_agent(RectangleSurveilAgent(heli, nw, se, feet(150)))

    heli.add_interface(Interface('wlan0', heli, wlan, 120))
    world.add_entity(heli)

print 'radar', len(world.get_entities())
radar = RadarSensor2(len(world.get_entities()), watts(6000), 25, 1, 5, 1, 3/360.0, 1)
radar.set_position(39.9485, -75.1325, 0)
world.add_entity(radar)

paths = [
    [feet(15), (39.9545, -75.1358, 0), (39.9432, -75.1363, 0), (39.9273, -75.1348, 0)],
    [feet(100), (39.9534, -75.1320, 0), (39.9374, -75.1367, 0), (39.9263, -75.1322, 0)],
    [feet(25), (39.9281, -75.1385, 0), (39.9416, -75.1393, 0), (39.9591, -75.1341, 0)],
    [feet(50), (39.9268, -75.1322, 0), (39.9333, -75.1340, 0), (39.9482, -75.1337, 0), (39.9583, -75.1322, 0)]
]

for path in paths :
    print 'boat', len(world.get_entities())
    e = Scripted(len(world.get_entities()), path[2:], path[0], 0)
    e.set_position(*path[1])
    world.add_entity(e)

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
