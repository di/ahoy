import pickle
import base64

def serialize(obj) :
    return base64.b64encode(pickle.dumps(obj, 2))

def unserialize(serialized) :
    return pickle.loads(base64.b64decode(serialized))
