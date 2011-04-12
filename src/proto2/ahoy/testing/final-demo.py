import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.sensors.radarsensor import RadarSensor
from ahoy.sensors.sonarsensor import SonarSensor
from ahoy.entities.scripted import Scripted
from ahoy.agents.rectanglesurveil import RectangleSurveilAgent
from ahoy.commsengines.logloss import LogLossComms
from ahoy.tcpforward import TcpForward
from ahoy.network import Network
from ahoy.interface import Interface
from ahoy.util.units import *

world = World()

sonar1n = Node(len(world.get_entities()))
sonar1n.set_position(39.8560599677, -75.255277528, 0)
sonar1n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
world.add_entity(sonar1n)

sonar2n = Node(len(world.get_entities()))
sonar2n.set_position(39.9103365806, -75.1257383781, 0)
sonar2n.add_sensor('sonar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
world.add_entity(sonar2n)

radarn = Node(len(world.get_entities()))
radarn.set_position(39.886597, -75.166043, 0)
radarn.add_sensor('radar', RadarSensor(trans_power=watts(6000), trans_freq=25, gain=1, aperature=5, prop_fact=1, dwell_time=3/360.0, angle=1))
world.add_entity(sonar2n)

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
