import asyncio
from saturn import protocol, config


class Server:
    def __init__(self, host, port,
                 tcp=True, udp=False):
        self.host = host
        self.port = port
        self.tcp = tcp
        self.udp = udp
        self.auth_methods = []

    def init_auth_methods(self):
        for method in config.AUTHENTICATION_METHODS:
            m = __import__(method, globals=globals(), fromlist=[''])
            self.auth_methods.append(m.Authenticator(**getattr(config, method.upper().replace('.', '_'), {})))


    @property
    def server_auth_methods(self):
        return [x.method for x in self.auth_methods]

    async def auth(self, method, *args, **kwargs):
        for m in self.auth_methods:
            if m.method == method:
                return await m.authenticate(*args, **kwargs)

    def start(self):
        loop = asyncio.new_event_loop()
        self.init_auth_methods()
        if self.tcp:
            loop.create_task(protocol.Socks5TcpServer(self, loop).start_server(self.host, self.port))
        loop.run_forever()


if __name__ == '__main__':
    server = Server('0.0.0.0', 8081)
    server.start()