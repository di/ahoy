import pickle
from ahoy.util.serialize import *

class Event :
    def __init__(self) :
        pass

    def pickle(self) :
        return serialize(self)

    @staticmethod
    def from_pickle(pickled) :
        return unserialize(pickled)
