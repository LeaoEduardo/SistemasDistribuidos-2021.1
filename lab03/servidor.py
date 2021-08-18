import socket
import json
import multiprocessing
import select
import sys
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

#define a lista de I/O de interesse (já inclui a entrada padrao)
entradas = [sys.stdin]
#armazena historico de conexoes
conexoes = {}

def iniciaServidor():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 
	# vincula a localizacao do servidor
	sock.bind((HOST, PORTA))
	# coloca-se em modo de espera por conexoes
	sock.listen(5) 
	# configura o socket para o modo nao-bloqueante
	# sock.setblocking(True)
	# inclui o socket principal na lista de entradas de interesse
	entradas.append(sock)

	return sock

def aceitaConexao(sock):
  '''Aceita o pedido de conexao de um cliente
  Entrada: o socket do servidor
  Saida: o novo socket da conexao e o endereco do cliente'''

  # estabelece conexao com o proximo cliente 
  clisock, endr = sock.accept()
  # registra a nova conexao
  conexoes[clisock] = endr

  return clisock, endr

def atendeRequisicoes(clisock, endr):
  '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
  Entrada: socket da conexao e endereco do cliente
  Saida: '''
  
  while True:
    #recebe dados do cliente
    data = clisock.recv(1024) 
    if not data: # dados vazios: cliente encerrou
      print(str(endr) + '-> encerrou')
      clisock.close() # encerra a conexao com o cliente
      return
    else: 
      msg = json.loads(data)

      file = search_file(msg["file"])
      if file != -1:
        number = occurrences(msg['word'].lower(), file)
      else:
        number = file

      answer = {
        "message" : number
      }

	  # print(str(endr) + ': ' + str(data, encoding='utf-8'))
    # envia mensagem de resposta
    clisock.send(bytes(json.dumps(answer), encoding='utf-8'))
		
def main():
  '''Inicializa e implementa o loop principal (infinito) do servidor'''
  clientes=[] #armazena os processos criados para fazer join
  sock = iniciaServidor()
  print("Pronto para receber conexoes...")
  print("Lista de comandos:")
  print("\t 'fim' para encerrar servidor\n\t 'hist' para ver todas as conexões")
  while True:
    #espera por qualquer entrada de interesse
    leitura, escrita, excecao = select.select(entradas, [], [])
    #tratar todas as entradas prontas
    for pronto in leitura:
      if pronto == sock:  #pedido novo de conexao
        clisock, endr = aceitaConexao(sock)
        print ('Conectado com: ', endr)
        #cria novo processo para atender o cliente
        cliente = multiprocessing.Process(target=atendeRequisicoes, args=(clisock,endr))
        cliente.start()
        clientes.append(cliente) #armazena a referencia da thread para usar com join()
      elif pronto == sys.stdin: #entrada padrao
        cmd = input()
        if cmd == 'fim': #solicitacao de finalizacao do servidor
          for c in clientes: #aguarda todos os processos terminarem
            c.join()
          sock.close()
          sys.exit()
        elif cmd == 'hist': #outro exemplo de comando para o servidor
          print(str(conexoes.values()))

if __name__ == "__main__":
  main()


# while True:
# 	# depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
#   raw_msg = novoSock.recv(1024) # argumento indica a qtde maxima de dados
#   if not raw_msg: 
#     break 
#   else: 
#     msg = json.loads(raw_msg)

#     file = search_file(msg["file"])
#     if file != -1:
#       number = occurrences(msg['word'], file)
#     else:
#       number = file

#     answer = {
#       "message" : number
#     }

# 	  # envia mensagem de resposta
#     novoSock.send(bytes(json.dumps(answer), encoding='utf-8')) 

# # fecha o socket da conexao
# novoSock.close() 

# # fecha o socket principal
# sock.close() 