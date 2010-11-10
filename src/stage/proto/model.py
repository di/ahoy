class Model :
    def __init__(self, **kwds) :
        self._dict = kwds

    def get(self, key) :
        return self._dict[key]

    def set(self, key, value) :
        self._dict[key] = value
