from ahoy.agent import Agent

class RoutingAgent(Agent) :
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def handle(self, event, iface) :
        pass
