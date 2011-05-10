from ahoy.event import Event

class PredatorMessage(Event) :
    def __init__(self, src_agent_uid, contents) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._contents = contents

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_contents(self) :
        return self._contents
