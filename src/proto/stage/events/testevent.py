from event import Event

class TestEvent(Event) :
    EVENT_ID = 'TEST'
    def __init__(self, arg1val, arg2val) :
        m = Model(arg1=arg1val, arg2=arg2val)
        Event.__init__(self, m)
