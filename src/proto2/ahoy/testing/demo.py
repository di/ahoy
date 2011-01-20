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

heli_locs = [(39.9490, -75.1374), (39.9407, -75.1351), (39.9581, -75.1310)]
for i, loc in enumerate(heli_locs) :
    heli = Node(i)
    heli.set_position(loc[0], loc[1], feet(i * 100))
    se = loc
    nw = (loc[0] + .004, loc[1] - .003)
    heli.add_agent(RectangleSurveilAgent(heli, nw, se, feet(75)))
    world.add_entity(heli)

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
