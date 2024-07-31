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
Fazer o spider das diretorias e fazer o parsing do output das outras. 
Pode ser que tenhamos tempo para fazer mais merdas ainda sobre o SMB.




### updated Goals.
+ Fazer a enumeração do SMB, qasi toda. 



### IDEAS
O domínio quando é associado a um objeto server, precisa de conseguir 
também manipulá-lo. Precisamos de saber uma boa forma de fazer isto. 

### IDEAS for tommorrow

## Work
O method do spidershares foi criado com sucesso. Falta fazermos o filtering.
- Confirma se quando um host passa para DC todos os serviços que ele tem 
ficam a saber que ele é DC.
	-> O que acontece é que se os serviços não existirem, eles são criados. 
	-> E agora são também associados ao domínio. Estes serviços no entanto 
	se não tiverem sido adicionados para um DC, não serão acedíveis pelo domain
	porque o domain não recebeu nada em concreto para saber que tinha novos.


### horas
