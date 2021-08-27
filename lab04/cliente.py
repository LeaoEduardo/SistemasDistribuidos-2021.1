import socket
import json

from pprint import pprint

from random import randint

from user import User

SERVER_HOST = 'localhost' #maquina onde está o servidor
SERVER_PORT = 5000 #porta onde servidor escuta

# cria socket
server_sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
server_sock.connect((SERVER_HOST, SERVER_PORT)) 
user_port = int(str(server_sock.recv(1024), encoding='utf-8'))
print(user_port)

user_name = input("What's your name? ")

user = User(name=user_name, port=randint(6000,10000))

available_users = []

def send_request_to_server(user, command):

    msg_dict = {
        "type" : "request",
        "source": user.address,
        "destiny" : (SERVER_HOST, SERVER_PORT),
        "command" : command,
        "message" : user.name
    }
    msg = json.dumps(msg_dict)

    server_sock.sendall(bytes(msg, encoding='utf-8'))

def receive_server_response():
    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    raw_answer = server_sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
    # imprime a mensagem recebida
    return json.loads(str(raw_answer,encoding='utf-8'))

while True:
    command = input("Type your command ")
    if command == 'open':
        send_request_to_server(user, command)
        answer = receive_server_response()
        available_users = answer["users"]
        pprint(answer)
        user.init_server()
        user.receive_connections(available_users)

    break
    
# encerra a conexao
sock.close() 
