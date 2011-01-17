import sys
import signal
from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node
from stage.commsengines.logloss import LogLossComms
from stage.agents.moving import MovingAgent
from stage.tcpforward import TcpForward
from stage.util.units import *

world = World()

n1 = Node(0)
n1.set_position(40, -75, feet(100))
n1.add_agent(MovingAgent(n1, 40.01, -75.01, kilometers(0.02), kilometers(0.08), 0))
world.add_entity(n1)

n2 = Node(1)
n2.set_position(40.01, -75.01, feet(100))
world.add_entity(n2)

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
