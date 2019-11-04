import logging

from . import protocol
from . import auth
from . import dispatcher
from . import engine
from . import socks
from . import state
from .version import __version__

logging.basicConfig(level=logging.INFO)

#
# def validate_config():
#     if hasattr(config, "ALLOWED_DESTINATIONS"):
#         ips = []
#         for ip in config.ALLOWED_DESTINATIONS:
#             ips.append(ip_network(ip))
#         config.ALLOWED_DESTINATIONS = ips
#
#
# validate_config()


def start_server(host, port, config):
    server = engine.Server(host, port, config)
    server.start()
