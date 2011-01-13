import sys
import signal
from stage.simulation import Simulation
from stage.world import World
from stage.entities.node import Node
from stage.commsengines.logloss import LogLossComms
from stage.agents.moving import MovingAgent
from stage.tcpforward import TcpForward

world = World()

n1 = Node(0)
n1.add_agent(MovingAgent(n1, 40, -75, 0.02, 32, 0))
n1.set_position(39.9534, -75.1912, 0.02)
world.add_entity(n1)

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
