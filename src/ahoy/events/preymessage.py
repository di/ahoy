from ahoy.event import Event

class PreyMessage(Event) :
    def __init__(self, src_agent_uid, alive) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._alive = alive

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def is_alive(self) :
        return self._alive
