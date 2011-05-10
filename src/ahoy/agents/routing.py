from ahoy.agent import Agent

class RoutingAgent(Agent) :
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def handle_delivery(self, event, iface) :
        pass

    def handle_forward(self, event, iface) :
        pass
