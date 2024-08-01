# Daily Report

## week goals
Acabar o RPC.
Acabar o SMB, acho que não há assim tanta coisa que precisemos de fazer.
Começar e ficar a meio do LDAP.
implementar o DHCP, acho que não será muito díficil obter a informação.

O objetivo é depois começarmos a ver mais a fundo o NMAP e coisas que ele oferece 
e a parte do metasploit que acho que também seria engraçado.


## Goals 

### Goals TODO
código:
+ [PASSAR_OS_OBJETOS] Vamos mudar a estrutura do código para o contexto enviar já os objetos em vez de os nomes, apenas (ver se vale a pena) o que está no filter objects e que vem com nomes e nao objetos.
+ [FILTEROBJECTS] Os filter objects não terem um dicionário mas sim os valores. 
+ [CONTEXT] O context deve ser um objeto para nos conseguimos estandardizar o que passsamos para os métodos e como passamos.
+ [DOMAIN_METHODS] Falta as Trusts
+ [DNS_HOSTNAME] Podemos extrair o bicho do root ldap 

métodos:
Saber o SID de um user. - lookupnames
Saber os nomes de todos os users que têm RID, mas não name.
Saber os rid's the todos os users que têm nome mas não RID. 
saber o conteúdo para um user específico - queryuser 

output:
Neste caso será qualquer coisa como domains/domain_name/msrpc/<msrpc-server-ip>/users/<user>/


### Goals hoje
Extrair o DNS hostname dos hosts através do root ldap.
- vamos fazer isso através do go-windapsearch. 
- depois podemos passar para o pywerview
DNS hostname e depois começar com o LDAP.




### updated Goals.
Vou arrumar com o windapsearch, fazer as procuras todas acho que é demasiado, mas os users, groups e computers e assim acho que consigo.
Posso também procurar as policies. 


O pywerview fica para a outra semana, também já entra na lista de coisas que é mais da rede.
Em relação aos shares do SMB também não sei como vamos apresentar a info.





## IDEAS
Colocarmos lá os users. 

### IDEAS for tommorrow
Mostrar as shares que encontrámos em cada SMB server.

Colocar os domains que são da mesma forest Na mesma forest. 
Para podermos usar essa informação.


## Work
Fiz o DNS hostname através do root ldap.
Resolvi o BUG dos objetos. quase 2 horas para isto.

coloquei a máquina a aceitar nós listarmos os users pelo ldap.
criei o método de listar os users.
Falta fazer o update da informação que temos sobre os users.
	-> acho que a dos users está feita. Falta Testar, soma e segue.
Falta mostrar as shares que há lá no bicho. 
	-> AHHHHHH, yes


### horas
