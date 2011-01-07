from stage.util.geo import *
from stage.commsengine import CommsEngine
from stage.events.communication import CommunicationRecvEvent

class BasicComms(CommsEngine) :
    def __init__(self) :
        CommsEngine.__init__(self)
        # This line is bad; distance should be defined in the interfaces.  For testing only, it is defined here.
        self._max_range = 0.08 #km ~250ft

    def _on_send(self, event) :
        source_uid = event.get_src()
        dests_uids = event.get_message().get_dests()

        valid_dests = set([])

        src_lat, src_lon, src_agl = self.get_simulation().get_world().get_entity(source_uid).get_position()
        for dest_uid in dests_uids :
            dest_lat, dest_lon, dest_agl = self.get_simulation().get_world().get_entity(dest_uid).get_position()
            distance = lin_distance(src_lat, src_lon, src_agl, dest_lat, dest_lon, dest_agl)
            if distance <= self._max_range :
                valid_dests.add(dest_uid)

        if len(valid_dests) > 0 :
            valid_dests = list(valid_dests)
            message = event.get_message()
            message.set_dests(valid_dests)
            self.get_event_api().publish(CommunicationRecvEvent(event.get_src(), message, event.get_network()))
