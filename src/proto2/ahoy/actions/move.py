from ahoy.action import Action

class MoveAction(Action):

    def __init__(self, node, lat, lon, alt):
        self._lat_move = lat
        self._lon_move = lon
        self._alt_move = alt
        self._entity = node

    def perform(self):
        lat, lon, alt = self._entity.get_position()
        print str(self._entity.get_uid()) + ' is at position ' + str(lat) + ' , ' + str(lon) + ' , ' + str(alt) 
        self._entity.set_position(self._lat_move + lat, self._lon_move + lon, self._alt_move + alt)

    def test(self):
        print 'hello'
