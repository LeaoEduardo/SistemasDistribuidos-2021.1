# Relatório final do laboratório 4

## Breve relato sobre aplicação
Embora ainda apresentando alguns _bugs_ de vez em quando, considero que o desenvolvimento da aplicação foi bem sucedido. Aqui vai um breve resumo:
- Foi disponibilizada uma interface gráfica usando o módulo tkinter de _widgets_. Apesar de bem simples, cumpre a maioria dos pontos descritos na definição do menu do projeto.
- A arquitetura de sistema híbrida foi implementada com sucesso.
- O usuário pode visualizar todas as mensagens que ele manda e que recebe de outros pares para quem enviou a mensagem.

## Diferenças da proposta inicial
- Optei por trabalhar com requisição/resposta entre usuários também, além de não manter conexões permanentes, isto é, toda vez que o usuário clica em `send` para enviar a mensagem é aberto um novo socket de conexão que envia a mensagem e logo depois fecha a conexão após recebimento da resposta. Portanto, isso fez com que:
  - Não fizesse mais sentido ter o `(conectado)` ao lado do nome do usuário na lista de usuários. 
  - Não precisasse mais de um botão de iniciar ou encerrar conexão.
  - Não precisasse de espaço com conexões atuais do usuário.
  - O usuário pode selecionar qualquer outro que esteja ativo para mandar uma mensagem.
  - Comando `end` deixou de fazer muito sentido já que todas as conexões são encerradas a cada mensagem trocada.
- Já com relação à arquitetura de software foi interessante trabalhar com objetos para facilitar o pensamento, apesar de manter as mesmas responsabilidades para cliente e servidor. A diferença é que dentro da parte de cliente, foi feito um objeto `User` para ajudar no desenvolvimento da aplicação.
- Adição de tag `users` no corpo das mensagens do servidor já que todas as comunicações com o servidor envolviam a lista de usuários de alguma forma.
- Mudança no formato de lista de usuários para:
  ```json
    [
      {
        'address': ['127.0.0.1', 37968],
        'open': ['localhost', 9701],
        'user': 'Joao'
      },
      {
        'address': ['127.0.0.1', 37978],
        'open': ['localhost', 9711],
        'user': 'Maria'
      },
      {
        'address': ['127.0.0.1', 37978],
        'open': ['localhost', 9721],
        'user': 'Pedro'
      },
    ]
  ```
  No qual o `address` é o endereço pelo qual ele estabeleceu a conexão com o servidor e o `open` passou a ser a porta que ele abriu para receber conexões de seus _peers_.
- Outra mudança foi a de que não utilizei a estratégia de cabeçalho dizendo tamanho da mensagem, mas me prendi ao _request/response_ como no HTTP.

## Comentários finais
Não há dúvidas de que não foi um trabalho simples de fazer. Para mim, especificamente, fica o pensamento de que provavelmente teria sido mais simples se eu trabalhasse com uma arquitetura pura de cliente/servidor na qual o servidor encaminharia as mensagens. 

Porém, decidi por manter o P2P entre usuários por ser algo diferente dos outros laboratórios e mais desafiador para mim. 

Gostaria de ter tido mais tempo para sanar os pequenos _bugs_ que ficaram, mas com certeza foi um dos projetos mais interessantes que pude fazer no meu tempo de faculdade. 

Outra coisa que talvez tenha tomado mais tempo que o necessário foi a de que eu desenvolvi toda a aplicação pensando em fazer um `backend` com a interface do terminal para depois construir a interface gráfica e expandir para esse lado. Apesar de ter me feito pensar mais, tive que me desfazer de bastante código para a adaptação ao desenvolvimento com a interface gráfica. Acho que se já tivesse desenvolvido pensando nos dois lados teria perdido menos tempo.

Mas, no geral, considero que tenha sido um bom trabalho.