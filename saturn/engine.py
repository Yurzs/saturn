import asyncio
from saturn import protocol


class Server:
    def __init__(self, host, port,
                 tcp=True, udp=False,
                 auth=False,
                 auth_gssapi=False,
                 auth_user_pass=False):
        self.host = host
        self.port = port
        self.tcp = tcp
        self.udp = udp
        self.auth_methods = []
        self.auth_methods.append(0) if not auth else ''
        self.auth_methods.append(1) if auth_gssapi else ''
        self.auth_methods.append(2) if auth_user_pass else ''

    def start(self):
        loop = asyncio.new_event_loop()
        if self.tcp:
            loop.create_task(protocol.Socks5TcpServer(self, loop).start_server(self.host, self.port))
        loop.run_forever()


if __name__ == '__main__':
    server = Server('0.0.0.0', 8080)
    server.start()