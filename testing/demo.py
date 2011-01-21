import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.entities.radarsensor2 import RadarSensor2
from ahoy.agents.rectanglesurveil import RectangleSurveilAgent
from ahoy.commsengines.logloss import LogLossComms
from ahoy.tcpforward import TcpForward
from ahoy.network import Network
from ahoy.interface import Interface
from ahoy.util.units import *

world = World()

wlan = Network('wlan0')
world.add_network(wlan)

heli_areas = [(39.9558, -75.1386, 39.9475, -75.1314), (39.9468, -75.1396, 39.9419, -75.1314), (39.9410, -75.1420, 39.9360, -75.1321)]
for i, loc in enumerate(heli_areas) :
    heli = Node(i)
    heli.set_position(loc[0], loc[1], feet(i * 100))
    nw = (loc[0], loc[1])
    se = (loc[2], loc[3])
    heli.add_agent(RectangleSurveilAgent(heli, nw, se, feet(150)))

    heli.add_interface(Interface('wlan0', heli, wlan, 100))
    world.add_entity(heli)

radar = RadarSensor2(len(heli_areas), watts(6000), 25, 1, 5, 1, 3/360.0, 1)
radar.set_position(39.9485, -75.1325, 0)
world.add_entity(radar)

if __name__ == '__main__' :
    sim = Simulation(world, LogLossComms(), TcpForward(int(sys.argv[1])))

    def quit(signal, frame) :
        print 'Stopping...'
        sim.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    sim.start(2)

    while True :
        pass
