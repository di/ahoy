import subprocess
import sys

class Simulation :
    def __init__(self, scen_def, net_def, tic=None) :
        self._events = {}
        self._running = True
        self._time = 0
        self._tic = tic
        self._scen_def = scen_def
        self._net_def = net_def

    def stop(self) :
        self._running = False

    def initialize(self) :
        scenmod = __import__(scen_def.split('.')[0])
        scenario = getattr(scenmod, scen_def.split('.')[1])()
        for node_model in scenario.get_nodes() :
            subprocess.Popen(('python node.py ' + node_model.__str__()).split(' '))

    def add_event(self, time, event) :
        if not self._events.has_key(time) :
            self._events[time] = []
        self._events[time].append(event)

    def start(self) :
        while self._running :
            if len(self._events) > 0 :
                if tic != None :
                    for time in filter(lambda t : t <= self._time, self._events) :
                        for e in self._events[next] :
                            e.invoke()
                        del self._events[next]
                    if self._events.size() > 0 :
                        time.sleep(1.0)
                        self._time += 1.0
                else :
                    next = min(self._events.keys())
                    self._time = next
                    for e in self._events[next] :
                        e.invoke()
                    del self._events[next]

if __name__ == '__main__' :
    scen_def, net_def = sys.argv[1:]
    s = Simulation(scen_def, net_def)
    s.initialize()
    s.start()
