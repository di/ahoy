import subprocess
import sys
import time
from stage.api import API
from stage.event import Event
from stage.model import Model

class Simulation :
    def __init__(self, scen_def, net_def) :
        self._scen_def = scen_def
        self._net_def = net_def
        self._api = API('simulation')
        self._api.get_event_channel().subscribe('*', self._event_callback)

        self._scen_inst = None
        self._net_inst = None

    def _event_callback(self, event) :
        if event.get_type() == 'SENT' :
            self._api.get_event_channel().publish(Event('RECV', event.get_model()))
        else if event.get_type() == 'MOVEREQ' :
            self._scen_def.get_nodes()[event.get_model().get('name')].get_model().set('position', event.get_model().get('pos'))
            self._api.send('MOVEACPT', Model(name=event.get_model().get('name'), pos=event.get_model().get('pos')))

    def stop(self) :
        self._running = False

    def start(self) :
        scenmod = __import__(scen_def.split('.')[0])
        self._scen_inst = getattr(scenmod, scen_def.split('.')[1])()

        netmod = __import__(net_def.split('.')[0])
        self._net_inst = getattr(netmod, net_def.split('.')[1])(self._scen_inst)
        
        for node_model in self._scen_inst.get_nodes() :
            subprocess.Popen(('python node.py ' + node_model.__str__()).split(' '))

        time.sleep(1)
        self._api.get_event_channel().publish(Event('start', Model()))

        while True :
            pass
            
if __name__ == '__main__' :
    scen_def, net_def = sys.argv[1:]
    s = Simulation(scen_def, net_def)
    s.start()
