from stage.eventapi import EventAPI

class Entity :
    def __init__(self, ueid) :
        self._event_api = EventAPI()
        self._uid = iuid

    def get_event_api(self) :
        return self._event_api

    def get_uid(self) :
        return self._uid
