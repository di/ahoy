class Interface :
    def __init__(self, mac_address) :
        self._mac_address = mac_address
        self._ip = None
        self._subnetmask = None

    def get_mac(self) :
        return self._mac_address

    def get_ip(self) :
        return self._ip

    def set_ip(self, ip) :
        self._ip = ip

    def set_subnetmask(self, mask) :
        self._mask = mask
