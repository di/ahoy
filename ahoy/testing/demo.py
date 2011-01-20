import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.commsengines.logloss import LogLossComms
from ahoy.tcpforward import TcpForward
from ahoy.util.units import *
from ahoy.agents.rectanglesurveil import RectangleSurveilAgent

world = World()

base = Node(0)
base.set_position(39.9490, -75.1391, 0)
base.add_agent(RectangleSurveilAgent(base, (39.9495, -75.1390), (39.9441, -75.1321), feet(74)))
world.add_entity(base)

'''
heli_locs = [(39.9490, -75.1374), (39.9407, -75.1351), (39.9581, -75.1310)]
for i, loc in enumerate(heli_locs) :
    heli = Node(i + 1)
    heli.set_position(loc[0], loc[1], feet(i * 100))
    heli.add_agent(RectangleSurveil())
'''

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
