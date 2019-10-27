# Socks5 async proxy server
Saturn is a SOCKS5 server based on asyncio protocols
## Installation
### From [pypi.org](https://pypi.org/project/saturn-proxy-server/)
```bash
pip install saturn-proxy-server
```
### From this repo
```bash
git clone https://git.best-service.online/yurzs/saturn.git
cd saturn
python3 ./setup.py install
```
## Usage
Please edit `config.py` file before starting your server.  
By default proxying allowed to all hosts (`ALLOWED_DESTINATIONS =  ["0.0.0.0/0"]`).  You can specify single IP addresses 
(both IPv4 and IPv6) and subnets. 
```python3
import saturn
saturn.config.ALLOWED_DESTINATIONS = ["192.168.1.0/24"]
saturn.config.AUTHENTICATION_METHODS = ["saturn.auth.none"]
saturn.start_server("127.0.0.1", 8080) 
```
This config will allow passwordless connections with allowed proxying for `192.168.1.0-192.169.1.255` IP range.
You can use multiple auth methods at once like `["saturn.auth.none", saturn.auth.dict"]`
## Authentication methods
Current SOCKS5 standart supports
- [x] None ["saturn.auth.none"]
- [ ] GSSAPI ["saturn.auth.gssapi"]
- [x] Login/Password (dict format) ["saturn.auth.dict"]
### Custom authentication methods
You can implement your own authentication method (Login/Password)  
All you need to do is to implement `Authenticator` class with `async def authenticate(self, data)` method which will return `bool`
authentication result. Then just import your module and use it in config  
`saturn.config.AUTHENTICATION_METHODS = ["your_auth_method"]`
You can see examples in `saturn.auth`

### TODO list
- [ ] Logging
- [ ] Max socket limit
- [ ] More tests