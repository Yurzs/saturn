import argparse
import os

from saturn.engine import Server

parser = argparse.ArgumentParser(description='Start Saturn SOCKS5 server', usage="python3 -m saturn [options]")


parser.add_argument('--host', type=str,
                    help='IP address on which server will run (default: 0.0.0.0)', default='0.0.0.0')
parser.add_argument('--port', type=int,
                    help='port on which server will run (default: 8080)', default=8080)
parser.add_argument('--config', type=str, help='path to custom config file. Overrides --host and --port values',
                    default=os.path.dirname(__file__) + "/config.ini")

args = parser.parse_args()


def start_server(host, port, config):
    server = Server(host, port, config)
    server.start()


start_server(**args.__dict__)
