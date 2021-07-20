import socket
# Exemplo basico socket (lado ativo)

import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

while True:
  msg = input("Digite sua mensagem (\"close\" para encerrar):\n")
  # envia uma mensagem para o par conectado
  if msg == "close":
    break
  sock.send(bytes(msg,encoding="utf-8"))
  #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
  echo = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
  # imprime a mensagem recebida
  print(str(echo,  encoding='utf-8'))

# encerra a conexao
sock.close() 