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




## IDEAS


### IDEAS for tommorrow


## Work



### horas