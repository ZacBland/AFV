import json


class Packet(dict):

    @classmethod
    def from_bytearray(cls, array):
        return cls(json.loads(array))

    def __init__(self, *arg, **kw):
        super(Packet, self).__init__(*arg, **kw)

    def to_bytearray(self):
        return json.dumps(self).encode('utf-8')


if __name__ == "__main__":
    import sys
    packet = Packet()
    packet["first"] = 1
    packet["second"] = 2
    print("before", packet.to_bytearray(), "sizeof:", sys.getsizeof(packet.to_bytearray()))

    byte_packet = Packet.from_bytearray(packet.to_bytearray())
    print("after", byte_packet, "sizeof:", sys.getsizeof(byte_packet.to_bytearray()))
