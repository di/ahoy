import signal
import sys
import subprocess
from ahoy.eventapi import EventAPI
from ahoy.events.startup import *

class StartupDaemon :
    def __init__(self, phys_id) :
        self._event_api = EventAPI()
        self._event_api.start()
        self._phys_id = phys_id
        self._running_pids = set([])
        self._running = True

    def _on_startup(self, event) :
        self.terminate_all()
        self._event_api.unsubscribe_all(StartupEvent)
        self._event_api.subscribe(StartSimulationEvent, self._on_sim_start)
        self._event_api.publish(AckStartupEvent(self._phys_id))
        self._world = event.get_world()

    def terminate_all(self) :
        for p in self._running_pids :
            p.kill()
        self._running_pids.clear()

    def _start_entity_process(self, entity) :
        print 'Starting subprocess for uid %s' % entity.get_uid()
        p = subprocess.Popen(('python entity.py %s %s' % (entity.pickle(), self._world.pickle())).split(' '))
        self._running_pids.add(p)

    def _on_sim_start(self, event) :
        local_entities = event.get_mapping()[self._phys_id]
        for e in local_entities :
            self._start_entity_process(e)

    def start(self) :
        self._event_api.subscribe(StartupEvent, self._on_startup)
        self._event_api.subscribe(StopSimulationEvent, self._restart)
        while self._running :
            pass

    def _restart(self, event) :
        self.terminate_all()
        self._event_api.clear_subscriptions()
        self._running_pids = set([])

        print 'Got stop event.  State cleared.'
        self._event_api.subscribe(StartupEvent, self._on_startup)
        self._event_api.subscribe(StopSimulationEvent, self._restart)

    def stop(self) :
        self._event_api.stop()
        self.terminate_all()
        self._running = False

if __name__ == '__main__' :
    d = StartupDaemon(sys.argv[1])
    print 'Starting as %s' % (sys.argv[1],)

    def quit(signal, frame) :
        print 'Stopping...'
        d.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, quit)

    d.start()
