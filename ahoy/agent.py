from threading import Thread

class Agent :
    def __init__(self, owner_node) :
        self._owner_node = owner_node

    def get_owner_node(self) :
        return self._owner_node

    def start(self) :
        t = Thread(target=self.run)
        t.start()
        return t
     
    def run(self) :
        pass
