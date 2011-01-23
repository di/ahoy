from ahoy.entity import Entity

class Scripted(Entity) :
    def __init__(self, uid, waypoints, vel, vert_vel) :
        Entity.__init__(self, uid)
        self._waypoints = waypoints
        self._vel = vel
        self._vert_vel = vert_vel

    def run(self) :
        for dest in self._waypoints :
            print 'moving to', dest
            self.move(dest[0], dest[1], dest[2], self._vel, self._vert_vel, True)
            print 'done'
