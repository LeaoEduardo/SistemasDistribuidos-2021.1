import socket
import json
import threading
import sys
import select

from pprint import pprint

from variables import SERVER_HOST, SERVER_PORT

class User():

    def __init__(self, name, server_sock, port, host='', entries=[sys.stdin], connections={}, clients=[]):
        self.name = name
        self.address = (host, port)
        self.entries = entries
        self.connections = connections
        self.clients = clients
        self.server_sock = server_sock
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
        self.connections[clisock] = address

        return clisock, address

    def handle_requests(self, clisock, address):
        '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida: '''
        
        while True:
            #recebe dados do cliente
            data = clisock.recv(1024) 
            if not data: # dados vazios: cliente encerrou
                print(str(address) + '-> encerrou')
                clisock.close() # encerra a conexao com o cliente
                return
            else: 
                msg = json.loads(data) 
                pprint(msg)
                if msg["type"] == "p2p":
                    if msg["command"] == 'connect':
                        pass
                    elif msg["command"] == 'send':
                        pass
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
                    print ('Connected to: ', address)
                    #cria novo processo para atender o cliente
                    client = threading.Thread(target=self.handle_requests, args=(clisock,address))
                    client.start()
                    self.clients.append(client) #armazena a referencia da thread para usar com join()
                elif ready == sys.stdin: #entrada padrao
                    command = input("Type your command")
                    if command == 'close': #solicitacao de finalizacao do servidor
                        for c in self.clients: #aguarda todos os processos terminarem
                            c.join()
                        self.sock.close()
                        return
                    elif command == 'connect':
                        self.send_request_to_server(user=self, command='show')
                        response = self.receive_server_response()
                        available_users = response["users"]
                        print(available_users)
                        other_user = available_users[int(input("Index of user you want to connect: "))]
                        newSock = socket.socket()
                        newSock.connect((other_user["open"][0], other_user["open"][1]))

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

    
