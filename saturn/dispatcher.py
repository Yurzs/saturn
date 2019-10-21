from saturn import state
from saturn.socks import SocksTcpRequest, SocksHello, SocksAuthenticate


class Dispatcher:
    def __init__(self, server, loop, protocol, transport):
        self.server_transport = transport
        self.server = server
        self.loop = loop
        self.client_transport = None
        self.state = state.NotAuthenticated()
        self.busy = False
        self.previous = None

    async def handle(self, data):
        result = None
        # if (not isinstance(self.state, state.Connected) or not isinstance(self.state, state.Authenticated)) and \
        #         data[0] == 5 and len(data) == data[1] + 2:
        #     self.state = state.NotAuthenticated()
        if isinstance(self.state, state.Connected):
            self.client_transport.write(data)
        elif isinstance(self.state, state.NotAuthenticated):
            result = SocksHello(self, data).reply()
        elif isinstance(self.state, state.WaitingAuthenticationData) and data[0] == 1:
            result = await SocksAuthenticate(self, data).authenticate()
        elif isinstance(self.state, state.Authenticated) and data[0] == 5 and len(data) >=10:
            request = SocksTcpRequest.parse(self, data)
            result = await request.go()
        return result

    def reply(self, data):
        self.server_transport.write(data)