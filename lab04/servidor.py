import socket
import json
import threading
import select
import sys
from pprint import pprint

from user import User

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORT = 5000  # PORT onde chegarao as mensagens para essa aplicacao

#define a lista de I/O de interesse (já inclui a entrada padrao)
entries = [sys.stdin]
#armazena historico de conexoes
connections = {}

users = []

def init_server():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 
	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))
	# coloca-se em modo de espera por conexoes
	sock.listen(5) 
	# configura o socket para o modo nao-bloqueante
	# sock.setblocking(True)
	# inclui o socket principal na lista de entradas de interesse
	entries.append(sock)

	return sock

def accept_connection(sock):
    '''Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente'''

    # estabelece conexao com o proximo cliente 
    clisock, address = sock.accept()
    # registra a nova conexao
    connections[clisock] = address

    return clisock, address

def send(clisock, address, command, message='', type_msg='response'):
    ''' 
    Envia resposta ao cliente
    '''

    global users

    msg_dict = {
        "type" : type_msg,
        "source" : ['localhost', PORT],
        "destiny" : address,
        "command" : command,
        "users" : users,
        "message" : message
    }
    clisock.sendall(bytes(json.dumps(msg_dict), encoding='utf-8'))

def broadcast_users_list():
    for sock in connections:
        send(sock, connections[sock],'update',type_msg='request')
        data = sock.recv(1024)
        if not data:
            print(str(connections[sock]) + '-> encerrou')
            for user in users:
                if user["address"] == connections[sock]:
                    remove_active_user(sock, user["address"], user["user"])
            sock.close() # encerra a conexao com o cliente


def handle_requests(clisock, address):
    '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente
    Saida: '''
    
    while True:
        #recebe dados do cliente
        data = clisock.recv(1024) 
        if not data: # dados vazios: cliente encerrou
            print(str(address) + '-> encerrou')
            for user in users:
                if user["address"] == address:
                    remove_active_user(clisock, user["address"], user["user"])
            clisock.close() # encerra a conexao com o cliente
            return
        else: 
            msg = json.loads(data) 
            pprint(msg)
            if msg["type"] == "response":
                pass
            elif msg["type"] == "request":
                if msg["command"] == 'open':
                    add_active_user(clisock, address, msg["source"], msg["message"])
                    broadcast_users_list()
                elif msg["command"] == 'close':
                    try:
                        remove_active_user(clisock, address, msg["message"])
                        broadcast_users_list()
                    except BrokenPipeError:
                        pass
                elif msg["command"] == 'show':
                    send(clisock, address, 'show', '', type_msg='request')
                elif msg["command"] == 'update':
                    pass
            else:
                print("Error: message must be of type 'request' or 'response'")



def add_active_user(clisock, address, source, name):

    global users

    msg = "SUCCESS"

    for user in users:
        if user["user"] == name:
            msg = "FAILED: username already exists"
            send(clisock, address, "open", msg)
            clisock.close()
            return

    users.append({
        "user": name,
        "address": address,
        "open": source
    })
    print("Active users list:")
    pprint(users)
    send(clisock, address, "open", msg)

def remove_active_user(clisock, address, name):

    global users

    for user in users:
        if user["user"] == name and user["address"] == address:
            users.remove(user)
            break
    print("Active users list:")
    pprint(users)
    send(clisock, address, "close", "SUCCESS")

def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
    clients=[] #armazena os processos criados para fazer join
    sock = init_server()
    print("Ready to receive connections...")
    print("Command list:")
    print("\t 'finish' to end server\n\t 'show' to see all connections")
    while True:
        #espera por qualquer entrada de interesse
        readList, _, _ = select.select(entries, [], [])
        #tratar todas as entradas prontas
        for ready in readList:
            if ready == sock:  #pedido novo de conexao
                clisock, address = accept_connection(sock)
                print ('Connected to: ', address)
                #cria novo processo para atender o cliente
                client = threading.Thread(target=handle_requests, args=(clisock,address))
                client.start()
                clients.append(client) #armazena a referencia da thread para usar com join()
            elif ready == sys.stdin: #entrada padrao
                cmd = input()
                if cmd == 'finish': #solicitacao de finalizacao do servidor
                    for c in clients: #aguarda todos os processos terminarem
                        c.join()
                    sock.close()
                    sys.exit()
                elif cmd == 'show':
                    pprint(users)
                

if __name__ == "__main__":
    main()