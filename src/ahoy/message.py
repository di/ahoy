class Message :
    def __init__(self, payload, dest_agent) :
        self._payload = payload
        self._dest_agent = dest_agent

    def get_payload(self) :
        return self._payload

    def get_dest_agent(self) :
        return self._dest_agent

    def set_dest_agents(self, dest_agent) :
        self._dest_agents = dest_agents
