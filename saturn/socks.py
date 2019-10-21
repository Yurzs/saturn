from ipaddress import IPv6Address, IPv4Address, AddressValueError
from saturn import state
from saturn.protocol.client_tcp import TcpClient
from saturn import protocol, config
import socket
import random
from ipaddress import ip_network

class SocksPacket:
    def __init__(self, data):
        # assert data[0] == 5
        self.ver = 5


class SocksHello(SocksPacket):
    def __init__(self, dispatcher,  data):
        super().__init__(data)
        self.dispatcher = dispatcher
        self.nmethods = data[1]
        self.methods = [x for x in data[2:2 + self.nmethods]]

    def reply(self):
        for m in self.dispatcher.server.server_auth_methods:
            if m in self.methods:
                self.dispatcher.state = state.WaitingAuthenticationData(method=m) if not m == 0 else state.Authenticated()
                return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(m, 1, byteorder='big')
        return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(255, 1, byteorder='big')


class SocksAuthenticate:
    def __init__(self, dispatcher, data):
        self.data = data
        self.dispatcher = dispatcher
        self.server = dispatcher.server

    async def authenticate(self):
        if await self.server.auth(self.dispatcher.state.method, self.data):
            self.dispatcher.state = state.Authenticated()
            return int(1).to_bytes(1, byteorder='big') + int(0).to_bytes(1, byteorder='big')
        return int(1).to_bytes(1, byteorder='big') + int(10).to_bytes(1, byteorder='big')


class SocksTcpRequest:

    @staticmethod
    def parse(dispatcher, data):
        assert data[0] == 5
        if data[1] == 1:
            return SocksRequestConnect(dispatcher, data)
        elif data[1] == 2:
            return SocksRequestBind(dispatcher, data)
        elif data[1] == 3:
            return SocksRequestUdpAssociate(dispatcher, data)
        return


class SocksRequest:
    def __init__(self,dispatcher, data):
        self.dispatcher = dispatcher
        self.ver = data[0]
        self.cmd = data[1]
        self.rsv = data[2]
        self.atyp = data[3]
        if self.atyp == 1:
            self.dst_addr = IPv4Address(data[4:-2])
        elif self.atyp == 3:
            self.dst_addr = data[5:5 + data[4]].decode()
        elif self.atyp == 4:
            self.dst_addr = IPv6Address(data[4:-2])
        self.dst_port = int.from_bytes(data[-2:], byteorder='big')

    async def go(self):
        pass

class SocksRequestConnect(SocksRequest):

    async def go(self):
        assert not isinstance(self.dispatcher.state, state.Connected)
        on_connect = self.dispatcher.loop.create_future()
        allowed_to = False
        for addr in getattr(config, 'ALLOWED_DESTINATIONS', [ip_network('0.0.0.0/0')]):
            if self.dst_addr in ip_network(addr):
                allowed_to = True
                break
        if not allowed_to:
            return SocksTcpReply(self.dispatcher, 5, 2, 0, 1, int(IPv4Address('0.0.0.0')), 0)
        try:
            self.dispatcher.client_transport, self.client_protocol = await self.dispatcher.loop.create_connection(
                lambda: TcpClient(self.dispatcher, on_connect),
                str(self.dst_addr), self.dst_port)
        except OSError as e:
            if e.errno == 110:
                return SocksTcpReply(self.dispatcher, 5, 3, 0, 1, int(IPv4Address('0.0.0.0')), 0)
            if e.errno == 111:
                return SocksTcpReply(self.dispatcher, 5, 5, 0, 1, int(IPv4Address('0.0.0.0')), 0)
            if e.errno == 113 or e.errno == 101:
                return SocksTcpReply(self.dispatcher, 5, 4, 0, 1, int(IPv4Address('0.0.0.0')), 0)
            if e.errno == 22:
                return SocksTcpReply(self.dispatcher, 5, 8, 0, 1, int(IPv4Address('0.0.0.0')), 0)
            print('ERROR ',e.errno, e)
            return SocksTcpReply(self.dispatcher, 5, 1, 0, 1, int(IPv4Address('0.0.0.0')), 0)
        self.dispatcher.connected = True
        await on_connect
        self.dispatcher.state = state.Connected()
        return SocksTcpReply(self.dispatcher, 5, 0, 0, 1, int(IPv4Address(socket.gethostbyname(socket.gethostname()))),
                             8081)


class SocksRequestBind(SocksRequest):

    def __init__(self, dispatcher, data):
        assert len(data) >= 10
        super().__init__(dispatcher, data)

    async def go(self):
        on_connect = self.dispatcher.loop.create_future()
        try:
            self.dispatcher.client_transport, self.client_protocol = await self.dispatcher.loop.create_connection(
                lambda: TcpClient(self.dispatcher, on_connect),
                str(self.dst_addr), self.dst_port)
        except OSError as e:
            print(e.errno, e)
        try:
            port = random.randrange(30000, 65535)
            self.dispatcher.loop.create_task(protocol.TcpServer(self, self.dispatcher.loop).start_server(self.host, port))
        except OSError as e:
            print(e.errno, e)
        return SocksTcpReply(self.dispatcher, 5, 0, 0, 1, int(IPv4Address(socket.gethostbyname(socket.gethostname()))), port)


class SocksRequestUdpAssociate(SocksRequest):
    async def go(self):
        print('wooops2')


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
