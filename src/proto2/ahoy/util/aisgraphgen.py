import random
import time
import networkx

class AISDataGen():
    def __init__(self, data=None):
     
        if(data == None):   
            self.file_ = "AIS_probs.dat"
        else:
            self.file_ = data
        self.graph_ = networkx.Graph()
        self.initialize()


    #Reads in the values to the probs dict
    def initialize(self):
        n = 0
        file = open(self.file_,'r')
        for line in file:
            line = line.rstrip('\n')
            data = line.split(':')
            self._addTransition(data)
            n += 1
            print str(n)

    #adds a transition to the probs dict
    #data is a list of lat,lon,and probability of reaching 
    #that state. 
    def _addTransition(self, data):
    	nodes = data[:2]
    	weight = float(data[2])
    	self.graph_.add_nodes_from(nodes)



#This section was for testing

#loc = [39.881592,-75.172737]
datagen = AISDataGen()
#loc = [39.860668, -75.224197]
#while(True):
#    print loc
#    loc = datagen.get_next_location(loc[0],loc[1])
#    time.sleep(2)
