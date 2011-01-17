from ahoy.event import Event

class DataEvent(Event) :
    def __init__(self, metric, dataset, indep, dep) :
        Event.__init__(self)
        self._metric = metric
        self._dataset = dataset
        self._indep = indep
        self._dep = dep
        self._extras = extras

    def get_metric(self) :
        return self._metric

    def get_dataset(self) :
        return self._dataset

    def get_indep(self) :
        return self._indep

    def get_dep(self) :
        return self._dep

    def get_extras(self) :
        return self._extras
