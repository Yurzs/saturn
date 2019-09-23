from ipaddress import IPv6Address, IPv4Address
from saturn.protocol.client_tcp import TcpClient


class SocksHello:
    def __init__(self, data):
        self.ver = data[0]
        assert self.ver == 5
        self.nmethods = data[1]
        self.methods = [x for x in data[2:2 + self.nmethods]]

    def reply(self, server):
        return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(0, 1, byteorder='big')


class SocksTcpRequest:
    def __init__(self, dispatcher, data):
        self.dispatcher = dispatcher
        assert data[0] == 5
        self.ver = data[0]
        self.cmd = data[1]
        self.rsv = data[2]
        self.atyp = data[3]
        if self.atyp == 1:
            self.dst_addr = IPv4Address(data[4:-2])
        elif self.atyp == 3:
            self.dst_addr = data[5:5+data[4]].decode()
        elif self.atyp == 4:
            self.dst_addr = IPv6Address(data[4:-2])
        self.dst_port = int.from_bytes(data[-2:], byteorder='big')

    async def connect(self):
        on_connect = self.dispatcher.loop.create_future()
        self.dispatcher.client_transport, self.client_protocol = await self.dispatcher.loop.create_connection(
            lambda: TcpClient(self.dispatcher, on_connect),
            str(self.dst_addr), self.dst_port)
        self.dispatcher.connected = True
        await on_connect
        return SocksTcpReply(self.dispatcher, 5, 0, 0, 1, int(IPv4Address('192.168.1.45')), 8080)


    async def bind(self):
        pass

    async def udp_associate(self):
        pass


class SocksTcpReply:
    def __init__(self, dispatcher, ver, rep, rsv, atyp, bind_addr, bind_port):
        self.dispatcher = dispatcher
        self.ver: int = ver
        self.rep: int = rep
        self.rsv: int = rsv
        self.atyp: int = atyp
        self.bind_addr: int = bind_addr
        self.bind_port: int = bind_port

    def __bytes__(self):
        return self.ver.to_bytes(1, byteorder='big') + \
            self.rep.to_bytes(1, byteorder='big') + \
            self.rsv.to_bytes(1, byteorder='big') + \
            self.atyp.to_bytes(1, byteorder='big') + \
            self.bind_addr.to_bytes(4, byteorder='big') + \
            self.bind_port.to_bytes(2, byteorder='big')