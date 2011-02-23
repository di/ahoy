import sys
import signal
from ahoy.world import World
from ahoy.commsengines.logloss import LogLossComms
from ahoy.simulation import Simulation
from ahoy.entities.node import Node
from ahoy.sensors.sonarsensor import SonarSensor
from ahoy.util.units import *

world = World()

node = Node(0)
node.add_sensor('radar', SonarSensor(source_level=220, source_bw=10, array_size=360, interval=5, min_snr=2))
#node.set_position(39.95324, -75.13752, 0) #west pylon
node.set_position(39.95102, -75.13517, 0) #middle river
#node.set_position(42.67205, -86.83878, 0)

world.add_entity(node)

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
