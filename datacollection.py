import sys
from ahoy.eventapi import EventAPI
from ahoy.events.data import DataEvent

class DataCollector :
    def __init__(self) :
        self._data = {}
        self._event_api = EventAPI()
        self._thread = self._event_api.start()
        self._event_api.subscribe(DataEvent, self._on_data)
        self._event_api.subscribe(StopSimulationEvent, self._on_stop)

    def _on_data(self, event) :
        if not self._data.has_key(event.get_metric()) :
            self._data[event.get_metric()] = {}

        if not self._data[event.get_metric()].has_key(event.get_dataset()) :
            self._data[event.get_metric()][event.get_dataset()] = {}

        self._data[event.get_metric()][event.get_dataset()][event.get_indep()] = event.get_dep()

    def _on_stop(self, event) :
        self._event_api.stop()

    def get_thread(self) :
        return self._thread

    def get_data(self) :
        return self._data

if __name__ == '__main__' :
    path = sys.argv[1]
    dc = DataCollector()
    dc.get_thread().join()

    for metric, datasets in dc.get_data().iteritems() :
        f = open('%s/%s.data' % (path, metric), 'w')
        for dataset in datasets.keys() :
            for indep in sorted(datasets[dataset].keys()) :
                f.write('%s %s\n' % (indep, datasets[dataset][indep]))
        f.write('\n')
        f.close()
