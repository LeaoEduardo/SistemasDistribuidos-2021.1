import socket
import json
import threading
import sys
import select
import time

from pprint import pprint

from variables import SERVER_HOST, SERVER_PORT

class User():

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
        '''Aceita o pedido de conexao de um cliente
        Entrada: o socket do servidor
        Saida: o novo socket da conexao e o endereco do cliente'''

        # estabelece conexao com o proximo cliente 
        clisock, address = self.sock.accept()
        # registra a nova conexao
        self.connections[address] = clisock

        return clisock, address

    def handle_requests(self, clisock, address):
        '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida: '''
        
        while True:
            #recebe dados do cliente
            try:
                data = clisock.recv(1024) 
            except ConnectionResetError:
                pass
            if not data: # dados vazios: cliente encerrou
                clisock.close() # encerra a conexao com o cliente
                return
            else: 
                msg = json.loads(data) 
                # pprint(msg)
                if msg["type"] == "p2p":
                    if msg["command"] == 'send':
                        print(msg["message"])
                    elif msg["command"] == 'end':
                        pass
                else:
                    print("Error: message must be of type 'p2p'")

    def receive_connections(self, available_users):
        while True:
            #espera por qualquer entrada de interesse
            readList, _, _ = select.select(self.entries, [], [])
            #tratar todas as entradas prontas
            for ready in readList:
                if ready == self.sock:  #pedido novo de conexao
                    clisock, address = self.accept_connection()
                    # print ('Connected to: ', address)
                    #cria novo processo para atender o cliente
                    client = threading.Thread(target=self.handle_requests, args=(clisock,address))
                    client.start()
                    self.clients.append(client) #armazena a referencia da thread para usar com join()
                elif ready == sys.stdin: #entrada padrao
                    command = input()
                    if command == 'close': #solicitacao de finalizacao do servidor
                        for c in self.clients: #aguarda todos os processos terminarem
                            c.join()
                        self.sock.close()
                        return
                    elif command == 'show peers':
                        pprint(self.peers)
                    elif command == 'show connections':
                        pprint(self.connections)
                    elif command == 'send':
                        available_users = self.get_available_users()
                        print([available_user["user"] for available_user in available_users])
                        other_user = self.get_user(input("Name of user you want to connect: "), available_users)
                        self.connect_p2p(other_user)
                        peer_name = other_user["user"]
                        peer_address = self.peers.get(peer_name)
                        message = f"({self.name}): " + input("Type your message: \n")
                        self.send_request_to_peer(peer_address=peer_address, command='send', message=message)
                        self.close_socket(peer_name, peer_address)

    def close_socket(self, peer_name, peer_address):
        self.connections[peer_address].close()
        del self.connections[peer_address]
        del self.peers[peer_name]

    def get_user(self, username, available_users):
        while True:
            for user in available_users:
                if user["user"] == username:
                    return user
            print("User not found, please try again")
            username = input()
        

    def add_peer(self, name, address):
        self.peers[name] = address

    def get_available_users(self):
        self.send_request_to_server(user=self, command='show')
        response = self.receive_server_response()
        return [user for user in response["users"] if user["user"] != self.name]
    
    def connect_p2p(self, other_user):
        newSock = socket.socket()
        newSock.connect((other_user["open"][0], other_user["open"][1]))
        peer_address = newSock.getpeername()
        self.peers[other_user["user"]] = peer_address
        # print("Peers:")
        # pprint(self.peers)
        self.connections[peer_address] = newSock
        # print("Connections:")
        # pprint(self.connections)

    def send_request_to_peer(self, peer_address, command, message, destiny_sock=None):

        msg_dict = {
            "type" : "p2p",
            "source": (SERVER_HOST, self.address[1]),
            "destiny" : peer_address,
            "command" : command,
            "message" : message
        }
        msg = json.dumps(msg_dict)

        if destiny_sock is None:
            destiny_sock = self.connections.get(peer_address, "ERROR")
            if destiny_sock == 'ERROR':
                print("SOCKET NOT VALID: ", peer_address, " not found")
                return
        
        destiny_sock.sendall(bytes(msg, encoding='utf-8'))

    def send_request_to_server(self, user, command):

        msg_dict = {
            "type" : "request",
            "source": [SERVER_HOST, user.address[1]],
            "destiny" : (SERVER_HOST, SERVER_PORT),
            "command" : command,
            "message" : user.name
        }
        msg = json.dumps(msg_dict)

        self.server_sock.sendall(bytes(msg, encoding='utf-8'))
    
    def receive_server_response(self):
        #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
        raw_answer = self.server_sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
        # imprime a mensagem recebida
        return json.loads(str(raw_answer,encoding='utf-8'))

    
