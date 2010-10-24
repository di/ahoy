from threading import Thread
from application import Application

class Node :
    def __init__(self, id) :
        self._id = id
        self._interfaces = {}
        self._applications = []
        self._routing_table = RoutingTable()

    def add_interface(self, name, iface) :
        self._interfaces[name] = iface

    def add_application(self, application) :
        application.set_node(self)
        self._applications.append(application)

    def start(self) :
        for application in self._applications :
            application.start()
