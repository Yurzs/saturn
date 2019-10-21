from . import protocol
from . import dispatcher
from . import engine
from . import socks
from . import auth
from . import config
from ipaddress import ip_network

def validate_config():
    if hasattr(config, 'ALLOWED_DESTINATIONS'):
        ips = []
        for ip in config.ALLOWED_DESTINATIONS:
            ips.append(ip_network(ip))
        config.ALLOWED_DESTINATIONS = ips

validate_config()

def start_server(host='0.0.0.0', port=8080):
    server = engine.Server(host, port)
    server.start()