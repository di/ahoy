import pickle

class Event :
    def __init__(self) :
        pass

    def pickle(self) :
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled) :
        return pickle.loads(pickled)
