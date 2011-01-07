class Message :
    def __init__(self, payload, dests) :
        self._payload = payload
        if type(dests) != list :
            self._dests = [ dests ]

    def get_payload(self) :
        return self._payload

    def get_dests(self) :
        return self._dests
