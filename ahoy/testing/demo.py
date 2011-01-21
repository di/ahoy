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

heli_locs = [(39.9558, -75.1386, 39.9475, -5.1314), (39.9468, -75.1396, 39.9419, -75.1314), (39.9410, -75.1420, 39.9360, -75.1321)]
for i, loc in enumerate(heli_locs) :
    heli = Node(i)
    heli.set_position(loc[0], loc[1], feet(i * 100))
    nw = (loc[0], loc[1])
    se = (loc[2], loc[3])
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
