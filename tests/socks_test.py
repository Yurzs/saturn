import unittest
import saturn
import asyncio
from configparser import ConfigParser


class ServerTests(unittest.TestCase):

    def test_auth_methods(self):
        self.assertRaises(TypeError, saturn.engine.Server)
        # server = saturn.engine.Server()


class SocksTests(unittest.TestCase):

    def test_hello_none_auth(self):
        with open("tmp_config.ini", "w") as tmp_config:
            config = ConfigParser()
            config.add_section("Authentication")
            config.set("Authentication", "methods", "saturn.auth.none")
            config.write(tmp_config)
        server = saturn.engine.Server("127.0.0.1", 1, config_path="tmp_config.ini")
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b"\x05\x02\x00\x02").reply()
        self.assertEqual(b"\x05\x00", bytes(hello))
        hello = saturn.socks.SocksHello(dispatcher, b"\x05\x01\x02").reply()
        self.assertEqual(b"\x05\xff", bytes(hello))

    def test_hello_only_password(self):
        with open("tmp_config.ini", "w") as tmp_config:
            config = ConfigParser()
            config.add_section("Authentication")
            config.add_section("Users")
            config.set("Authentication", "methods", "saturn.auth.dict")
            config.write(tmp_config)
        server = saturn.engine.Server("127.0.0.1", 1, config_path="tmp_config.ini")
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b"\x05\x01\x00").reply()
        self.assertEqual(bytes(hello), b"\x05\xff")
        hello = saturn.socks.SocksHello(dispatcher, b"\x05\x01\x02").reply()
        self.assertEqual(bytes(hello), b"\x05\x02")

    def test_hello_unknown(self):
        with open("tmp_config.ini", "w") as tmp_config:
            config = ConfigParser()
            config.add_section("Authentication")
            config.add_section("Users")
            config.set("Authentication", "methods", "saturn.auth.dict")
            config.write(tmp_config)
        server = saturn.engine.Server("127.0.0.1", 1, config_path="tmp_config.ini")
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b"\x05\x01\x05").reply()
        self.assertEqual(bytes(hello), b"\x05\xff")

    def test_no_auth_methods(self):
        with open("tmp_config.ini", "w") as tmp_config:
            config = ConfigParser()
            config.add_section("Authentication")
            config.set("Authentication", "methods", "")
            config.write(tmp_config)
        server = saturn.engine.Server("127.0.0.1", 1, config_path="tmp_config.ini")
        self.assertRaises(Exception, server.init_auth_methods)

    def test_SocksAuthenticate(self):
        with open("tmp_config.ini", "w") as tmp_config:
            config = ConfigParser()
            config.add_section("Authentication")
            config.add_section("Users")
            config.set("Authentication", "methods", "saturn.auth.dict")
            config.set("Users", "default_user", "someDefaultPassword")
            config.write(tmp_config)
        server = saturn.engine.Server("127.0.0.1", 1, config_path="tmp_config.ini")
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        dispatcher.state = saturn.state.WaitingAuthenticationData(2)
        login = "default_user"
        password = "someDefaultPassword"
        req = b"\x05" + len(login).to_bytes(1, "big") + login.encode() + len(password).to_bytes(1, "big") + password.encode()
        self.assertEqual(b"\x01\x00", asyncio.run(saturn.socks.SocksAuthenticate(dispatcher, req).authenticate()))

