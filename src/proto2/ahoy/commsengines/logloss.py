from ahoy.util.geo import *
from ahoy.entities.node import Node
from ahoy.commsengine import CommsEngine
from ahoy.events.communication import CommunicationRecvEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.link import LinkEvent

class LogLossComms(CommsEngine) :
    def __init__(self) :
        CommsEngine.__init__(self)
        self.get_event_api().subscribe(EntityMoveEvent, self._on_movement)

    def _get_rx_power(self, src_uid, dest_uid, src_power) :
        src_lat, src_lon, src_agl = self.get_world().get_entity(src_uid).get_position()
        dest_lat, dest_lon, dest_agl = self.get_world().get_entity(dest_uid).get_position()
        distance = lin_distance(src_lat, src_lon, src_agl, dest_lat, dest_lon, dest_agl)

        # TODO: These parameters should be in the interface, not here.
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
        if self._get_rx_power(src_uid, dest_uid, src_power) <= -recv_sensitivity :
            return False
        return True

    def _on_send(self, event) :
        source_node_uid = self.get_node_from_agent(event.get_src_agent_uid())
        src_power = self.get_world().get_entity(source_node_uid).get_interface_on_net(event.get_network())['power']

        recvrs = set([])
        for iface in self.get_world().get_network(event.get_network()).get_interfaces() :
            node = iface.get_owner()
            dest_node_uid = node.get_uid()
            if source_node_uid != dest_node_uid :
                dest_power = node.get_interface_on_net(event.get_network())['power']
                if self._should_deliver(source_node_uid, dest_node_uid, src_power, dest_power) :
                    recvrs.add(node.get_uid())
        self.get_event_api().publish(CommunicationRecvEvent(event.get_src_agent_uid(), recvrs, event.get_message(), event.get_network()))

    # TODO: BEST. METHOD. EVER.   Change this...
    # Simplify some of these if's...
    def _on_movement(self, event) :
        move_uid = event.get_uid()
        for entity in self.get_world().get_entities() :
            if isinstance(entity, Node) :
                if move_uid != entity.get_uid() :
                    for iface in entity.get_interfaces() :
                        network = self.get_world().get_network(iface.get_network_name())
                        if network.both_in_network(move_uid, entity.get_uid()) :
                            src_power = self.get_world().get_entity(move_uid).get_interface_on_net(network.get_name())['power']
                            dest_power = self.get_world().get_entity(entity.get_uid()).get_interface_on_net(network.get_name())['power']
                            if self._should_deliver(move_uid, entity.get_uid(), src_power, dest_power) :
                                pathloss = self._get_rx_power(move_uid, entity.get_uid(), src_power)
                                if network.check_cache(move_uid, entity.get_uid(), pathloss) :
                                    self.get_event_api().publish(LinkEvent(True, move_uid, entity.get_uid(), network.get_name(), pathloss))
                            else :
                                if network.check_cache(move_uid, entity.get_uid()) :
                                    self.get_event_api().publish(LinkEvent(False, move_uid, entity.get_uid(), network.get_name()))
