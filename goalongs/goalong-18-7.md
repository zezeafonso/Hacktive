# Daily Report

## Goals
Implementar irmos ver novos comandos apenas quando íamos para fechar o programa. Se calhar desta forma acabamos por poupar 
tempo. Podemos depois ver outras estratégias.



### updated Goals.
- 

### Coisas ainda por fazer
+ [PASSAR_OS_OBJETOS] Vamos mudar a estrutura do código para o contexto enviar já os objetos em vez de os nomes, apenas (ver se vale a pena) o que está no filter objects e que vem com nomes e nao objetos.
+ [FILTEROBJECTS] Os filter objects não terem um dicionário mmas sim os valores. 
+ [CONTEXT] O context deve ser um objeto para nos conseguimos estandardizar o que passsamos para os métodos e como passamos.
+ [DOMAIN_METHODS] os restantes métodos do domain.


### IDEAS
[especificando o context]
Neste caso o que podíamos fazer era cada pedaço do get context muito provavelmente está ligado a uma set de métodos específica. Quando há uma alteração desse componente iamos ver a set específica de comandos específicos dele para apenas analisarmos esses métodos/comandos e não todos.

[Generalizando os métodos]
No caso de generalizar os métodos, vamos verificar todos os métodos e todos os get_contexts.
Havia uma questão de se comandos duplicados iam ser chamados ou não.

Esta operação é apenas para lançar novos comandos. Ou seja pegar no estado atual e ver se fez diferença para os comandos que podemos lançar, não afeta de facto o estado dos objetos. Apenas vamos ver se é para lançar novos ou não. 
Para isso talvez possamos usar uma set global de objetos que foram modificados. 
Quando formos para acabar o programa vamos ver se essa set está limpa. Se não estiver vamos a cada um deles e verificamos o seu estado se é para correr novos comandos ou não. 
Eu quero apenas ir à set de objetos que lá estava ao ínicio por isso provavelmente vamos copiar a set quando a encontramos no ínicio e apenas vamos a esses objetos, de forma a que: 
caso haja comandos que entretanto corram e modifiquem novos objetos não vai afetar a nossa lista de objetos para verificar. Caso contrário esta operação podia ser muito longa. 
Parece me bem.

### IDEAS for tommorrow




## Work
+ já percebi como vamos fazer e já tá implementado as funções que vão chamar a set de updated objects. 
Agora o objetivo seria quando de facto atualizamos um objeto colocá-lo lá.
Onde estiver o check_for_updates é colocar o objeto lá.
+ parece me estar feito. Também tirei a parte dos dependent objects

### horas
