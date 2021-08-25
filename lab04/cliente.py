import socket
import json

from pprint import pprint

SEVER_HOST = 'localhost' #maquina onde está o servidor
SERVER_PORT = 5000 #porta onde servidor escuta

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((SEVER_HOST, SERVER_PORT)) 

user_name = input("What's your name? ")

while True:

    command = input("Type your command ")

    msg_dict = {
        "type" : "request",
        "destiny" : f"{SEVER_HOST}:{SERVER_PORT}",
        "command" : command,
        "message" : user_name
    }

    msg = json.dumps(msg_dict)

    sock.sendall(bytes(msg, encoding='utf-8'))
    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    raw_answer = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
    # imprime a mensagem recebida
    answer = json.loads(str(raw_answer,encoding='utf-8'))

    pprint(answer)

    if command == 'close':
        break

# encerra a conexao
sock.close() 
