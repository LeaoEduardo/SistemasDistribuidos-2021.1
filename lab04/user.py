import socket
import json
import threading
import sys
import select

from pprint import pprint

from variables import SERVER_HOST, SERVER_PORT

class User:

    def __init__(self, name, server_sock, port, host='', entries=[sys.stdin], connections={}, clients=[], peers={}):
        self.name = name
        self.address = (host, port)
        self.entries = entries
        self.connections = connections
        self.clients = clients
        self.server_sock = server_sock
        self.peers = peers
        self.sock = socket.socket()

    def __str__(self):
        return self.name

    def init_server(self):
        self.sock.bind(self.address)
        self.sock.listen(5)
        self.entries.append(self.sock)
        print("Ready to receive connections...")

    def accept_connection(self):

        clisock, address = self.sock.accept()
        self.sock.setblocking(False)
        self.connections[address] = clisock

        return clisock, address

    def close_socket(self, peer_name, peer_address):
        self.connections[peer_address].close()
        del self.connections[peer_address]
        del self.peers[peer_name] 
