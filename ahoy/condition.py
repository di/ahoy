class Condition:
    def __init__(self):
        pass

    # This function is extended in sub classes. If its true
    # then the condition is met
    def is_met(self, event):
        return True
