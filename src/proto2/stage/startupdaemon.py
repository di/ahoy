from stage.eventapi import EventAPI

class StartupDaemon :
    def __init__(self, phys_id) :
        self._event_api = EventAPI()
        self._phys_id = phys_id

        self._event_api.subscrube(StartupEvent, self._on_startup)

    def _on_startup(self, event) :
        self._terminate_all()


    def _terminate_all(self) :
        #TODO: Kill all existing node processes
        pass
