import socks

s = socks.socksocket()
s.set_proxy(socks.SOCKS5, "localhost", 8080)
s.connect(("vk.com", 443))
s.sendall(b"GET / HTTP/1.1 ...")
print(s.recv(4096))