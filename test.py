import socks
for _ in range(500):
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, "localhost", 8081, username='test_user', password='Test_password')
    s.connect(("127.0.0.1", 8080))
    s.sendall(b"GET / HTTP/1.1 ...")
    print(s.recv(4096))