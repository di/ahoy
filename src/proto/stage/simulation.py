import subprocess
import sys

class Simulation :
    def __init__(self, scen_def, net_def) :
        self._scen_def = scen_def
        self._net_def = net_def

    def stop(self) :
        self._running = False

    def start(self) :
        scenmod = __import__(scen_def.split('.')[0])
        scenario = getattr(scenmod, scen_def.split('.')[1])()

        netmod = __import__(net_def.split('.')[0])
        net = getattr(netmod, net_def.split('.')[1])(scenario)
        
        for node_model in scenario.get_nodes() :
            print node_model.get('interfaces')
            subprocess.Popen(('python node.py ' + node_model.__str__()).split(' '))
        while True :
            pass
            
if __name__ == '__main__' :
    scen_def, net_def = sys.argv[1:]
    s = Simulation(scen_def, net_def)
    s.start()
