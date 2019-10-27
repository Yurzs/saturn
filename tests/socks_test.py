import unittest
import saturn
import asyncio

class ServerTests(unittest.TestCase):

    def test_auth_methods(self):
        self.assertRaises(TypeError, saturn.engine.Server)
        # server = saturn.engine.Server()

class SocksTests(unittest.TestCase):

    def test_hello_none_auth(self):
        server = saturn.engine.Server('127.0.0.1', 1, custom_auth=["saturn.auth.none"])
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b'\x05\x02\x00\x02').reply()
        self.assertEqual(b"\x05\x00", bytes(hello))
        hello = saturn.socks.SocksHello(dispatcher, b'\x05\x01\x02').reply()
        self.assertEqual(bytes(hello), b"\x05\xff")

    def test_hello_only_password(self):
        server = saturn.engine.Server('127.0.0.1', 1, custom_auth=["saturn.auth.dict"])
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b'\x05\x01\x00').reply()
        self.assertEqual(bytes(hello), b"\x05\xff")
        hello = saturn.socks.SocksHello(dispatcher, b'\x05\x01\x02').reply()
        self.assertEqual(bytes(hello), b"\x05\x02")

    def test_hello_unknown(self):
        server = saturn.engine.Server('127.0.0.1', 1, custom_auth=["saturn.auth.dict"])
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        hello = saturn.socks.SocksHello(dispatcher, b'\x05\x01\x05').reply()
        self.assertEqual(bytes(hello), b"\x05\xff")

    def test_no_auth_methods(self):
        server = saturn.engine.Server('127.0.0.1', 1, custom_auth=[])
        self.assertRaises(Exception, server.init_auth_methods)


    def test_SocksAuthenticate(self):
        server = saturn.engine.Server('127.0.0.1', 1, custom_auth=["saturn.auth.dict"])
        server.init_auth_methods()
        dispatcher = saturn.dispatcher.Dispatcher(server, None, None)
        dispatcher.state = saturn.state.WaitingAuthenticationData(2)
        login = 'USER_TEST'
        password = 'Test_password'
        req = b"\x05" + len(login).to_bytes(1, "big") + login.encode() + len(password).to_bytes(1, "big") + password.encode()
        self.assertEqual(b"\x01\x00", asyncio.run(saturn.socks.SocksAuthenticate(dispatcher, req).authenticate()))

