import random
import time

class AISDataGen():
    def __init__(self, data=None):
     
        self.probs_ = {}
        if(data == None):   
            self.file_ = "AIS_probs.dat"
        else:
            self.file_ = data

        #self.initialize()


    #Reads in the values to the probs dict
    def initialize(self):
        file = open(self.file_,'r')
        for line in file:
            line = line.rstrip('\n')
            data = line.split(':')
            self._addTransition(data)

    #adds a transition to the probs dict
    #data is a list of lat,lon,and probability of reaching 
    #that state. 
    def _addTransition(self, data):
        if(not (self.probs_.has_key(data[0]))):
            self.probs_[data[0]] = {}
        self.probs_[data[0]][data[1]] = float(data[2])



    def get_next_location(self, latfrom, lonfrom):
        key = str(latfrom) + "," + str(lonfrom)
        if(not self.probs_.has_key(key)):
            return [latfrom, lonfrom]

        else:
            to_loc = self.probs_[key].keys()
            rand = random.random()
            n = 0
            #only going to len(to_loc)-1 so that we can avoid the 
            #probabilities not adding up to 1 and getting 1 as our
            #random number
            for i in range(0,len(to_loc)-1):
                chance = self.probs_[key][to_loc[i]]
                n = n + chance
                if(n <= rand):
                    lat, lon = to_loc[i].split(',')
                    return [float(lat),float(lon)]

            #if we made it this far we know its the last location
            #that we need. 
            lat,lon = to_loc[len(to_loc)-1].split(',')
            return [float(lat),float(lon)]

#This section was for testing

#loc = [39.881592,-75.172737]
#datagen = AISDataGen()
#loc = [39.860668, -75.224197]
#while(True):
#    print loc
#    loc = datagen.get_next_location(loc[0],loc[1])
#    time.sleep(2)
