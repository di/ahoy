import sys
import subprocess
from stage.eventapi import EventAPI
from stage.events.startup import StartupEvent, StartSimulationEvent, AckStartupEvent

class StartupDaemon :
    def __init__(self, phys_id) :
        self._event_api = EventAPI()
        self._phys_id = phys_id

    def _on_startup(self, event) :
        self._terminate_all()
        self._event_api.unsubscribe_all(StartupEvent)
        print 'subscribing StartSimulationEvent'
        self._event_api.subscribe(StartSimulationEvent, self._on_sim_start)
        self._event_api.publish(AckStartupEvent(self._phys_id))

    def _terminate_all(self) :
        #TODO: Kill all existing node processes
        pass

    def _start_entity_process(self, entity) :
        print 'python entity.py %s' % entity.pickle()
        subprocess.Popen(('python entity.py %s' % entity.pickle()).split(' '))

    def _on_sim_start(self, event) :
        local_entities = event.get_mapping()[self._phys_id]
        for e in local_entities :
            self._start_entity_process(e)

    def start(self) :
        self._event_api.subscribe(StartupEvent, self._on_startup)
        while True :
            pass

if __name__ == '__main__' :
    d = StartupDaemon(sys.argv[1])
    print 'Starting as %s' % (sys.argv[1],)
    d.start()
