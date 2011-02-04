import sys
import signal
from ahoy.world import World
from ahoy.commsengines.logloss import LogLossComms
from ahoy.simulation import Simulation
from ahoy.entities.node import Node
from ahoy.sensors.radarsensor import RadarSensor
from ahoy.util.units import *

world = World()

node = Node(0)
node.add_sensor('radar', RadarSensor(node.get_uid(), watts(6000), 25, 1, 5, 1, 3/360.0, 1))
world.add_entity(node)

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
