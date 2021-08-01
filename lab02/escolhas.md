# Atividade 1

### Objetivo: Refinar a arquitetura de software — usando o estilo arquitetural em camadas — apresentada abaixo.

### Camadas:
1. Funcionalidades da camada de interface com o usuário: recebe do usuário o nome do arquivo e a palavra de busca e exibe na tela o resultado do processamento. O resultado do processamento poderá ser:
   1.  Uma mensagem de erro indicando que o arquivo nao foi encontrado; ou 
   2.  O número de ocorrências da palavra no arquivo. 
     
   As mensagens serão editadas nessa camada. 

2. Funcionalidades da camada de processamento: solicita o acesso ao arquivo texto. Se o arquivo for válido, realiza a busca pela palavra informada e prepara a resposta para ser devolvida para a camada de interface. Se o arquivo for inválido, responde com a mensagem de erro. 
   
   O resultado será entregue para a camada de interface em formato `dict` de `python` em que `number` é o número de ocorrências e `-1` é a resposta em caso de erro. do seguinte tipo:
```python
{
  "message": number | "-1"
}
```

3. Funcionalidades da camada de acesso aos dados: verifica se o arquivo existe em sua base. Se sim, devolve o seu conteudo inteiro. Caso contrário, devolve uma mensagem de erro.

# Atividade 2
### Objetivo: Refinar a proposta de instanciação da arquitetura de software da aplicação definida na Atividade 1 para uma arquitetura de sistema cliente/servidor de dois níveis, com um servidor e um cliente, apresentada abaixo. 

### Proposta de arquitetura de sistema:
1. Lado cliente: implementa a camada de interface com o usuário. O usuário poderá solicitar o processamento de uma ou mais buscas em uma única execução da aplicação: o programa espera pelo nome do arquivo e da palavra de busca, faz o processamento, retorna o resultado, e então aguarda um novo pedido de arquivo e palavra ou o comando de finalização.

2. Lado servidor: implementa a camada de processamento e a camada de acesso aos dados. Projete um servidor iterativo, isto é, que trata as requisições de um cliente de cada vez, em um unico fluxo de execução (estudaremos essa classificação depois). Terminada a interação com um cliente, ele poderá voltar a esperar por nova conexão. Dessa forma, o programa do servidor fica em loop infinito (depois veremos como lidar com isso).

Refinar:
1. Especificar os tipos e a sequencia de mensagens que serão trocadas entre cliente e servidor, considerando um comportamento requisição/resposta;
2. Definir as estruturas de dados que serão usadas e o conteúdo das mensagens que serão trocadas entre cliente e servidor;
3. Detalhar outras decisões de implementação do lado do cliente e do lado do servidor.

# Especificidades do projeto
- Foi escolhida a estrutura de dicionários `python` para enviar e receber as mensagens usando a biblioteca `json` como serializador.
- As camadas de processamento e acesso aos dados estão no lado do servidor em `servidor.py`, enquanto que a camada de interface do usuário está no lado do cliente em `cliente.py`.
- Por conta da base de dados escolhida, fez-se necessária uma interação com o usuário para busca dos documentos.