from ahoy.event import Event

class PreyMessage(Event) :
    def __init__(self, src_agent_uid, pos, alive) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._pos = pos
        self._alive = alive

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_pos(self) :
        return self._pos

    def is_alive(self) :
        return self._alive
