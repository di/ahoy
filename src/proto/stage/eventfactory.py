class EventFactory :
    @staticmethod
    def from_string(type, string) :
        return Event(type, Model.from_string(string))
    @staticmethod
    def make_test(arg1v, arg2v) :
        return Event('TEST', Model(arg1=arg1v, arg2=arg2v))
