import socket
import json

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

connection = True
while connection:
  command = False
  while command == False:
    doc_theme = input("Digite o número da área de interesse para a busca:\n \
    1. business\n \
    2. entertainment\n \
    3. politics\n \
    4. sport\n \
    5. tech\n \
    6. encerrar buscas\n")

    if doc_theme == "1":
      doc_theme = "business"
      command = True
    elif doc_theme == "2":
      doc_theme = "entertainment"
      command = True
    elif doc_theme == "3":
      doc_theme = "politics"
      command = True
    elif doc_theme == "4":
      doc_theme = "sport"
      command = True
    elif doc_theme == "5":
      doc_theme = "tech"
      command = True
    elif doc_theme == "6":
      command = True
      connection = False
    else:
      print("Comando não reconhecido. Tente novamente.")

  if connection == False:
    break

  doc_number = int(input("Digite o número do documento de interesse: "))
  word = input("Digite a palavra a ser buscada: ")

  if doc_number < 10:
    doc_name = doc_theme + f"/00{doc_number}.txt"
  elif doc_number < 100:  
    doc_name = doc_theme + f"/0{doc_number}.txt"
  else:
    doc_name = doc_theme + f"/{doc_number}.txt"

  msg_dict = {
    "file" : doc_name,
    "word" : word
    }

  msg = json.dumps(msg_dict)

  sock.send(bytes(msg, encoding='utf-8'))
  #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
  raw_answer = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
  # imprime a mensagem recebida
  answer = json.loads(str(raw_answer,encoding='utf-8'))

  if answer["message"] == -1:
    print("\nErro: Documento não encontrado\n")
  else:
    print(f"\nO número de ocorrências encontrado é de {answer['message']}\n")

# encerra a conexao
sock.close() 