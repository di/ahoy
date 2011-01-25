import sys
import signal
from ahoy.simulation import Simulation
from ahoy.world import World
from ahoy.entities.node import Node
from ahoy.commsengines.logloss import LogLossComms
from ahoy.agents.moving import MovingAgent
from ahoy.tcpforward import TcpForward
from ahoy.util.units import *

world = World()

n1 = Node(0)
n1.set_position(40, -75, feet(100))
n1.add_agent(MovingAgent(n1, 40.01, -75.01, feet(200), kilometers(0.08), feet(10)))
world.add_entity(n1)

n2 = Node(1)
n2.set_position(40.01, -75.01, feet(200))
world.add_entity(n2)

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
