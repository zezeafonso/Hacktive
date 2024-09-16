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

métodos:
Saber o SID de um user. - lookupnames
Saber os nomes de todos os users que têm RID, mas não name.
Saber os rid's the todos os users que têm nome mas não RID. 
saber o conteúdo para um user específico - queryuser 

output:
Neste caso será qualquer coisa como domains/domain_name/msrpc/<msrpc-server-ip>/users/<user>/


### Goals hoje
Fazer a enumeração ao SMB. 
Conseguir listar os shares com o user anónimo. 
Para cada share que consigamos fazer o spider. 




### updated Goals.
+ Fazer a enumeração do SMB, qasi toda. 



### IDEAS
Quando descobrimos que um host faz parte de um domínio podemos verificar um montão de coisas. 
Especialmente em relação aos serviços que ele já tem, pode ajudar bastante ao sabermos o domínio do bicho.
Para saber onde colocamos a informação e tudo mais. 
Pode ser importante saber onde verificamos as coisas. 

### IDEAS for tommorrow

## Work
Criei os métodos:
listshares -> lista as shares com o smbclient -L 
crackmapexec -> que nos dá se aceita a versão 1 e o smbsigning

faltam implementar os filters e updates destes manfios 
falta também fazer o spider das shares 


Do LDAP podemos usar bastante o windapsearch que acho que fica bom.

### horas
