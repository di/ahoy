from threading import Thread
from ahoy.action import Action
from ahoy.condition import Condition
from ahoy.entity import Entity
from ahoy.entities.node import Node

class Agent :
    def __init__(self, uid) :
        self._owner_node = None
        self._uid = uid
        self._behaviors = {}

    def get_uid(self) :
        return self._uid

    def get_owner_node(self) :
        return self._owner_node

    def set_owner_node(self, owner_node) :
        self._owner_node = owner_node

    def start(self) :
        self._init_behaviors()
        t = Thread(target=self.run)
        t.start()
        return t

    def on_message(self, event) :
        pass
     
    def run(self) :
        pass

    # add behavior to the self._behaviors list. 
    # event should be the class of the event cared about
    def add_behavior(self, behavior):
        precondition, event, action = behavior
        if not self._behaviors.has_key(event) :
            self._behaviors[event] = []
        
        self._behaviors[event].append([precondition,action])

    #remove a behavior from the self._behaviors list
    def remove_behavior(self, behavior):
        precondition, event, action = behavior
        if self._behaviors.has_key(event) :
            for p in self._behaviors[event]:
                mycondition, myaction = p
                if mycondition == precondition and myaction == action :
                    self._behaviors[event].remove(p)

    # check to see if there are behaviors for an event. If so check
    # to see if certain preconditions are met (always true for now)
    # if so, perform the action
    def _on_event(self, event):
        eventname = event.__class__
        if self._behaviors.has_key(eventname) :
            possible_actions = self._behaviors[eventname]
            for p in possible_actions :
                condition, action = p
                if condition.is_met(self, event) : 
                    action.perform()

    def _init_behaviors(self):
        for event in self._behaviors.keys():
            self.get_owner_node().get_event_api().subscribe(event, self._on_event)
