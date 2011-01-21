from threading import Thread
from ahoy.action import Action
from ahoy.condition import Condition

class Agent :
    def __init__(self, owner_node) :
        self._owner_node = owner_node
        self._behaviors = {}

    def get_owner_node(self) :
        return self._owner_node

    def start(self) :
        t = Thread(target=self.run)
        t.start()
        return t
     
    def run(self) :
        pass

    # add behavior to the self._behaviors list. 
    # event should be a string of the event's class name
    def add_behavior(self, behavior):
        precondition, event, action = behavior
        if(not self._behaviors.has_key(event)):
            self._behaviors[event] = []
        
        self._behaviors[event].append([precondition,action])

    #remove a behavior from the self._behaviors list
    def remove_behavior(self, behavior):
        precondition, event, action = behavior
        if(self._behaviors.has_key(event)):
            for p in self._behaviors[event]:
                mycondition, myaction = p
                if(mycondition == precondition and myaction == action):
                    self._behaviors[event].remove(p)

    # check to see if there are behaviors for an event. If so check
    # to see if certain preconditions are met (always true for now)
    # if so, perform the action
    def check_behavior(self, event):
        eventname = event.__class__.__name__
        if(self._behaviors.has_key(eventname)):
            possible_actions = self._behaviors[eventname]
            for p in possible_actions:
                condition, action = p
                if(condition.is_met('test')): #will always return true for now
                    action.perform()
    
