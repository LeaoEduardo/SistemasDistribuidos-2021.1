import socket
import json
from pathlib import Path

def search_file(doc_name: str):
  root_dir = Path("documentos")
  doc_path = root_dir / doc_name
  try:
    with open(doc_path, mode='r') as doc:
      txt = doc.read()
      return txt.lower()
  except OSError:
    return -1

def occurrences(word: str, file: str):
  return file.count(word)

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

# cria um socket para comunicacao
sock = socket.socket() # valores default: socket.AF_INET, socket.SOCK_STREAM  

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

# aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
print ('Conectado com: ', endereco)

while True:
	# depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
  raw_msg = novoSock.recv(1024) # argumento indica a qtde maxima de dados
  if not raw_msg: 
    break 
  else: 
    msg = json.loads(raw_msg)

    file = search_file(msg["file"])
    if file != -1:
      number = occurrences(msg['word'], file)
    else:
      number = file

    answer = {
      "message" : number
    }

	  # envia mensagem de resposta
    novoSock.send(bytes(json.dumps(answer), encoding='utf-8')) 

# fecha o socket da conexao
novoSock.close() 

# fecha o socket principal
sock.close() 