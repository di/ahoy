ethernet_header = Struct("ethernet_header",
    Nibble
    MacAddress("destination"),
    MacAddress("source"),
    Enum(UBInt16("type"),
        IPv4 = 0x0800,
        IPv6 = 0x86DD,
    ),
)
