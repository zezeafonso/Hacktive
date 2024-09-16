# Daily Report

## Goals
Put the code in order.

### updated Goals
- Vamos mudar a estrutura do código para os métodos, terem os filters associados.
- Vamos mudar a estrutura do código para que os métodos recebam apenas o contexto e não o NC.
- Vamos mudar a estrutura do código para o contexto enviar já os objetos em vez de os nomes, apenas
o que está no filter objects e que vem com nomes e nao objetos.
- Os filter objects não terem um dicionário mmas sim os valores. 
- colocar isto tudo a funcionar , vai ficar para amanhã também.

### IDEAS
[set para os objetos atualizados]
Em cada mini alteração vamos ver se os objetos foram alterados, ou colocamos uma referência ao objeto na tal set. No fim de corrermos todas as coisas/atualizações corremos o check_updates dos macacos que estão na set. 

[Eliminar os dependent objects]
Não há dependecias de informação por isso os dependent objects ão ter de ir à vida. 
Vemos isso no fim, de uma atualização completa. 
Também vai deixar de haver dependent objects, porque isso cria a tal questão

[Nova thread ou apenas correr qunado não há]
Se mesmo assim as atualizações ficarem lentas, 
podemos sempre verificar se há novos comandos ou não, 
apenas quando já não há mais filters ou comandos a correrem.
Desta forma garantimos que ele não perde tempo a verificar várias 
vezes atualizações ao mesmo objeto.

OU: usamos uma nova thread, mas que poderá fazer este trabalho de uma forma repetitiva.

### IDEAS for tommorrow
implement what's left.

* Implementar o output parsing chamar o filter correto associado aos métodos.
* Implementar que os updaters dos métodos chamem as funções de updates dos folders 
corretos. Desta forma podemos reaproveitar alguams coisas e fica também a fazer mais sentido.

Mais difícil:
* implementar a parte do verificar as changes que foram feitas com a tal set que vai guardar 
os objetos que foram atualizados, dessa forma vamos depois chamar todos os que foram atualizados
para se verificar se podemos chamar mais comandos ou não.



## Work
mudei os métodos filters e updaters para dentro das coisas. 
Acho que está melhor organizado assim.
Falta colocar as coisas a funcionar com esta nova maneira. 
Os updaters passam a ser associados com o método que foi usado. 

já meti os métodos a não usarem os NC's. 
É preciso parar de os usar nas threads. 
As threads também já não usam o bicho. 
Agora é fazer com que elas chamem o updater e o filter certo.

### horas

de manha 1 
antes da reuniao 1 e pouco
depois da reuniao 1 e meia.
