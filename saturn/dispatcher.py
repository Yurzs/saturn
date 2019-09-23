from saturn.socks import SocksTcpReply, SocksTcpRequest, SocksHello


class Dispatcher:
    def __init__(self, server, loop, protocol):
        self.server = server
        self.loop = loop
        self.server_protocol = protocol
        self.client_transport = None
        self.authenticated = False
        self.connected = False

    async def handle(self, data):
        if self.connected:
            self.client_transport.write(data)
            return
        if not self.authenticated:
            self.authenticated = True
            return SocksHello(data).reply(self.server)
        request = SocksTcpRequest(self, data)
        if request.cmd == 1:
            result = bytes(await request.connect())
            return result