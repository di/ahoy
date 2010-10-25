class EthernetLinkLayer(LinkLayer) :
    def __init__(self) :
        LinkLayer.__init__(self)

    def send(self, dest_ip, data) :
        mac = self._ip_to_mac(dest_ip)

