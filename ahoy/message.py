class Message :
    def __init__(self, payload, dest_agents) :
        self._payload = payload
        if type(dest_agents) != list :
            self._dest_agents = [ dest_agents ]
        else :
            self._dest_agents = dest_agents

    def get_payload(self) :
        return self._payload

    def get_dest_agents(self) :
        return self._dest_agents

    def set_dest_agents(self, dest_agents) :
        if type(dest_agents) != list :
            self._dest_agents = [ dest_agents ]
        else :
            self._dest_agents = dest_agents
