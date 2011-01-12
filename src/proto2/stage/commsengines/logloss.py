from stage.util.geo import *
from stage.entities.node import Node
from stage.commsengine import CommsEngine
from stage.events.communication import CommunicationRecvEvent
from stage.events.move import EntityMoveEvent
from stage.events.link import LinkEvent

class LogLossComms(CommsEngine) :
    def __init__(self) :
        CommsEngine.__init__(self)
        self.get_event_api().subscribe(EntityMoveEvent, self._on_movement)

    def _get_rx_power(self, src_uid, dest_uid, src_power) :
        src_lat, src_lon, src_agl = self.get_simulation().get_world().get_entity(src_uid).get_position()
        dest_lat, dest_lon, dest_agl = self.get_simulation().get_world().get_entity(dest_uid).get_position()
        distance = lin_distance(src_lat, src_lon, src_agl, dest_lat, dest_lon, dest_agl)

        d0 = 1.0 / 1000.0  # 1 meter
        ref_loss = 46.6777 # loss @ 1 meter
        l = 3.0 # path loss exponent
        flat_fade_factor = 0
        tx_power_dbm = 10 * math.log(src_power, 10)

        if distance <= d0 :
            return tx_power_dbm - ref_loss

        loss = -ref_loss - 10 * l * math.log(distance / d0, 10) + flat_fade_factor
        return tx_power_dbm + loss

    def _should_deliver(self, src_uid, dest_uid, src_power, recv_sensitivity) :
        if self._get_rx_power(src_uid, dest_uid, src_power) <= recv_sensitivity :
            return False
        return True

    def _on_send(self, event) :
        source_uid = event.get_src_node_uid()
        dests_uids = event.get_message().get_dests()

        valid_dests = set([])

        for dest_uid in dests_uids :
            src_power = self.get_simulation().get_world().get_entity(source_uid).get_interface(event.get_src_iface_name()).get_power()
            dest_power = self.get_simulation().get_world().get_entity(source_uid).get_interface_on_net(event.get_network()).get_power()
            if self._should_deliver(source_uid, dest_uid, src_power, dest_power) :
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
                            src_power = self.get_simulation().get_world().get_entity(move_uid).get_interface_on_net(network.get_name()).get_power()
                            dest_power = self.get_simulation().get_world().get_entity(entity.get_uid()).get_interface_on_net(network.get_name()).get_power()
                            # TODO: should probably cache the up/down status
                            if self._should_deliver(move_uid, entity.get_uid(), src_power, dest_power) :
                                pathloss = self._get_rx_power(move_uid, entity.get_uid(), src_power)
                                self.get_event_api().publish(LinkEvent(True, move_uid, entity.get_uid(), network.get_name(), pathloss))
                            else :
                                self.get_event_api().publish(LinkEvent(False, move_uid, entity.get_uid(), network.get_name()))
