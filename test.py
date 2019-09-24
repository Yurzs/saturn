import socks

for _ in range(500):
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, "localhost", 8081, username='test_user', password='Test_password')
    s.connect(("google.com", 80))
    s.sendall(b"GET / HTTP/1.1 ...")
    s.sendall(b"GET / HTTP/1.1 ...")
    s.close()
    print(s.recv(4096))