# Daily Report

## Goals
Implementar novos comandos do rpc, quantos mais melhor parece-me.

saber os grupos a que um user pertence.
Saber o SID de um user. - lookupnames
Saber os nomes de todos os users que têm RID, mas não name.
Saber os rid's the todos os users que têm nome mas não RID. 
saber o conteúdo para um user específico - queryuser 

+ Colocar os outputs por ordem. 
Neste caso será qualquer coisa como domains/domain_name/msrpc/<msrpc-server-ip>/users/<user>/



### updated Goals.
+ Saber o SID de um user. - lookupnames
+ saber o conteúdo para um user específico - queryuser (DONE)
+ saber os grupos a que um user pertence. (DONE)

### Coisas ainda por fazer
+ [PASSAR_OS_OBJETOS] Vamos mudar a estrutura do código para o contexto enviar já os objetos em vez de os nomes, apenas (ver se vale a pena) o que está no filter objects e que vem com nomes e nao objetos.
+ [FILTEROBJECTS] Os filter objects não terem um dicionário mmas sim os valores. 
+ [CONTEXT] O context deve ser um objeto para nos conseguimos estandardizar o que passsamos para os métodos e como passamos.
+ [DOMAIN_METHODS] Falta as Trusts


### IDEAS
Ou começamos a ver os netshares ou passamos para outras coisas 
(smb, ldap) 

sacar os SID's dos users e dos groups.

agora que encontrámos uma lista de Users, conseguimos fazer aquela treta do
impacket e verificar se ele tem um spn. 

começar a ver a parte do nmap. Queremos saber as coisas mais importantes.
Começar a ver a parte de listar as shares que conseguimos aceder

### IDEAS for tommorrow
podemos dar query ao ldap (com credentials mais facilmente usando o pywerview, não precisamos de especificar a ldap query)
 ./pywerview.py get-netuser -u samwell.tarly -p Heartsbane -w north.sevenkingdoms.local -t 192.168.56.11 --username sansa.stark


podemos saber os computadores que pertencem ao domínio
./pywerview.py get-netcomputer -u samwell.tarly -p Heartsbane -w north.sevenkingdoms.local --dc-ip  192.168.56.11

podemos enumerar as shares no computador que quisermos com as credenciais.
./pywerview.py get-netshare -u samwell.tarly -p Heartsbane -w north.sevenkingdoms.local --computername 192.168.56.11 

identificar as accounts que não precisam de pre-auth.
Ou fazemos ldapdump e sacamos a informação de lá!! Temos lá nas flags as contas que têm isso permitido
## Work


### horas
