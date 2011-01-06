import sys
from stage.simulation import Simulation

if __name__ == '__main__' :
    if len(sys.argv) < 2 :
        print ' usage: python simulation.py <worldfile.worldclass>'
        sys.exit(0)
    Simulation(sys.argv[1]).start(2)
