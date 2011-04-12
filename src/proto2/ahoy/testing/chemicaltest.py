import sys
import signal
from ahoy.world import World
from ahoy.commsengines.logloss import LogLossComms
from ahoy.simulation import Simulation
from ahoy.entities.node import Node
from ahoy.sensors.chemicalsensor import ChemicalSensor
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.agents.chemspillannounce import ChemicalSpillAnnounceAgent

world = World()

node = Node(0)
node.add_sensor('chemical', ChemicalSensor(interval=1))
node.set_position(39.883531, -75.193963, 0) #sw of navy yard
world.add_entity(node)

node1 = Node(1)
node1.add_sensor('chemical', ChemicalSensor(interval=1))
node1.set_position(39.890776,-75.195594, 0) #w of navy yard
world.add_entity(node1)

node2 = Node(2)
node2.set_position(39.892223,-75.196788, 0) #immediately east of I-95 bridge, on water
node2.add_agent( ChemicalSpillAnnounceAgent(2, 1, 4, 0.1) )   #ID, interval, announce time, spill rate in km/s
world.add_entity(node2)

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
