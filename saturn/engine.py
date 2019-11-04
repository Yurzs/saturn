import asyncio
import typing
import os
import logging

from ipaddress import IPv4Address, IPv6Address
from configparser import ConfigParser

from saturn import protocol


class Server:
    def __init__(self, host: typing.Union[IPv6Address, IPv4Address, str],
                 port: int, config_path: str = os.path.dirname(__file__) + "/config.ini",
                 tcp: bool = True, udp=False):
        self.config = ConfigParser()
        self.config.read(config_path)
        self.host = self.config.get("General", "host", fallback=None) or host if config_path else host
        self.port = self.config.get("General", "port", fallback=None) or port if config_path else port
        self.tcp = self.config.get("General", "tcp", fallback=None) or tcp if config_path else tcp
        self.udp = self.config.get("General", "udp", fallback=None) or udp if config_path else udp
        self.auth_methods = []

    def init_auth_methods(self):
        """
        Initiate authentication methods from independent modules
        :return:
        """
        for method in self.config["Authentication"].get("methods", "").split(","):
            m = __import__(method.strip(), globals=globals(), fromlist=[""])
            auth_method = m.Authenticator(**getattr(self.config, method.upper().replace(".", "_"), {}))
            if m.Authenticator.have_users:
                auth_method.import_users(self.config["Users"])
            self.auth_methods.append(auth_method)
        if not self.auth_methods:
            raise Exception("Server have no auth methods. Please fill in [Authentication] methods in config file")

    @property
    def server_auth_methods(self):
        """
        All auth methods IDs as list
        :return: list of auth methods IDs
        """
        return [x.method for x in self.auth_methods]

    async def auth(self, method, *args, **kwargs):
        """
        Router to authentication type authenticate() method
        :param method: int:
        :param args:
        :param kwargs:
        :return: bool: authenticated or not
        """
        for m in self.auth_methods:
            if m.method == method:
                return await m.authenticate(*args, **kwargs)
        else:
            return False

    def start(self):
        """
        Start SOCKS5 server
        :return:
        """
        logging.info("Starting Saturn SOCKS5 server")
        loop = asyncio.new_event_loop()
        self.init_auth_methods()
        if self.tcp:
            loop.create_task(protocol.Socks5TcpServer(self, loop).start_server(self.host, self.port))
        loop.run_forever()
