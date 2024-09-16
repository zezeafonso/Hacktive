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
+ [FILTEROBJECTS] Os filter objects não terem um dicionário mas sim os valores. 
+ [CONTEXT] O context deve ser um objeto para nos conseguimos estandardizar o que passsamos para os métodos e como passamos.
+ [DOMAIN_METHODS] Falta as Trusts
+ [DNS_HOSTNAME] Podemos extrair o bicho do root ldap, mas já extraímos do windapsearch da metadata.

métodos:
Saber o SID de um user. - lookupnames
Saber os nomes de todos os users que têm RID, mas não name.
Saber os rid's the todos os users que têm nome mas não RID. 
saber o conteúdo para um user específico - queryuser 

output:
Neste caso será qualquer coisa como domains/domain_name/msrpc/<msrpc-server-ip>/users/<user>/


### Goals hoje
ver o ldap do nmap.
Podemos extrair por lá muitos mais objetos que aqueles que extraímos,
pelo windapsearch. Se bem que o windapsearch deu uma boa.

à tarde:
fazer a parte do nmap, users, groups, computers do nmap.
fazer a parte das policies e cenas do windapsearch.
(em relação aos filters num sei).

Ainda falta no RPC vermos algumas coisas.



### updated Goals.
Vou arrumar com o windapsearch, fazer as procuras todas acho que é demasiado, mas os users, groups e computers e assim acho que consigo.
Posso também procurar as policies. 


O pywerview fica para a outra semana, também já entra na lista de coisas que é mais da rede.
Em relação aos shares do SMB também não sei como vamos apresentar a info.


## IDEAS
vamos melhorar o nmap como está para sacar as cenas do nmap.
Não me parece nada impossível.

### IDEAS for tommorrow
Mostrar as shares que encontrámos em cada SMB server.

Colocar os domains que são da mesma forest Na mesma forest. 
Para podermos usar essa informação.


## Work
vi o que o nmap conseguia fazer contra o ldap.

Ainda conseguiu sacar muita informação.


### horas
