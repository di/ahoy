from ahoy.util.geo import *
from ahoy.entities.node import Node
from ahoy.commsengine import CommsEngine
from ahoy.events.communication import CommunicationRecvEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.link import LinkEvent

class BasicComms(CommsEngine) :
    def __init__(self) :
        CommsEngine.__init__(self)
        self.get_event_api().subscribe(EntityMoveEvent, self._on_movement)
        # This line is bad; distance should be defined in the interfaces.  For testing only, it is defined here.
        self._max_range = 0.08 #km ~250ft

    def _in_range(self, source_uid, dest_uid) :
        src_lat, src_lon, src_agl = self.get_simulation().get_world().get_entity(source_uid).get_position()
        dest_lat, dest_lon, dest_agl = self.get_simulation().get_world().get_entity(dest_uid).get_position()
        distance = lin_distance(src_lat, src_lon, src_agl, dest_lat, dest_lon, dest_agl)

        if distance <= self._max_range :
            return True
        return False

    def _on_send(self, event) :
        source_uid = event.get_src_node_uid()
        dests_uids = event.get_message().get_dests()

        valid_dests = set([])

        for dest_uid in dests_uids :
            if self._in_range(source_uid, dest_uid) :
                valid_dests.add(dest_uid)

        if len(valid_dests) > 0 :
            valid_dests = list(valid_dests)
            message = event.get_message()
            message.set_dests(valid_dests)
            self.get_event_api().publish(CommunicationRecvEvent(event.get_src_node_uid(), event.get_src_iface_name(), message, event.get_network()))

    # TODO: BEST. METHOD. EVER.   Change this...
    def _on_movement(self, event) :
        move_uid = event.get_uid()
        for entity in self.get_simulation().get_world().get_entities() :
            if isinstance(entity, Node) :
                if move_uid != entity.get_uid() :
                    for iface in entity.get_interfaces() :
                        network = self.get_simulation().get_world().get_network(iface.get_network_name())
                        if network.both_in_network(move_uid, entity.get_uid()) :
                            # TODO: should probably cache the up/down status
                            if self._in_range(move_uid, entity.get_uid()) :
                                if network.check_cache(move_uid, entity.get_uid(), True) :
                                    self.get_event_api().publish(LinkEvent(True, move_uid, entity.get_uid(), network.get_name()))
                            else :
                                if network.check_cache(move_uid, entity.get_uid(), False) :
                                    self.get_event_api().publish(LinkEvent(False, move_uid, entity.get_uid(), network.get_name()))
