import asyncio
from saturn import socks
from ipaddress import IPv4Address, IPv6Address

class TcpServer(asyncio.Protocol):
    def __init__(self, dispatcher, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.dispatcher = dispatcher

    def connection_made(self, transport):
        self.transport = transport
        addr = IPv4Address(self.transport.get_extra_info('peername')[0])
        port = self.transport.get_extra_info('peername')[1]
        print(addr, port)
        self.dispatcher.server_transport.write(bytes(socks.SocksTcpReply(self.dispatcher,
                                                                            5, 0, 0, 1, int(addr), int(port))))

    def data_received(self, data: bytes) -> None:
        print('ooh data')
        self.dispatcher.client_transport.write(data)

    async def start_server(self, host='0.0.0.0', port=8080):
        server = await self.loop.create_server(
            lambda: self, host, port)
        async with server:
            await server.serve_forever()