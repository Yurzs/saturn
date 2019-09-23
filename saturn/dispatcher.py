from saturn import state
from saturn.socks import SocksTcpRequest, SocksHello, SocksAuthenticate


class Dispatcher:
    def __init__(self, server, loop, protocol):
        self.server = server
        self.loop = loop
        self.server_protocol = protocol
        self.client_transport = None
        self.state = state.NotAuthenticated()

    async def handle(self, data):
        if (not isinstance(self.state, state.Connected) or not isinstance(self.state, state.Authenticated)) and \
                data[0] == 5 and len(data) == data[1] + 2:
            self.state = state.NotAuthenticated()
        if isinstance(self.state, state.Connected):
            self.client_transport.write(data)
        elif isinstance(self.state, state.NotAuthenticated):
            return SocksHello(self, data).reply(self.server)
        elif isinstance(self.state, state.WaitingAuthenticationData):
            return await SocksAuthenticate(self, data).authenticate()
        elif isinstance(self.state, state.Authenticated):
            request = SocksTcpRequest(self, data)
            if request.cmd == 1:
                result = bytes(await request.connect())
                return result
