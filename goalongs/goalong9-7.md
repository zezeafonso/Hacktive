# Daily Report

## Goals
To finish RPC enumeration and then improve the code structure. 

### updated Goals
Use more threads to check for the updates in state. Or do this in just one thread but change the way we check for methods or state, because like this, each update takes a lot of time to happen since we're checking for so much irrelevant information.

### IDEAS
Podemos usar threads, mas mesmo assim precisávamos de melhorar como chamamos os métodos. Os métodos podiam ser atributos dos Network Components, mas nesse caso também não sei se ganhava muito há métodos que podem ser chamados mais que uma vez e produzir diferentes comandos. Todos os comandos que usam um input que dependa de informação que obtemos. 
Onde eu acho que podemos estar a perder tempo é: colocar comandos desnecessários na queue e depois verificar se já foram corridos ou não, porque de facto estamos a constuir comandos que não era preciso correrem outra vez.

Acho que o estado em si, não causa um processo muito lento, mas colocar os eventos queue e ver se eles já foram lançados ou não talvez isso demore. Porque estamos a fazer isso para vários comandos e até mais que uma vez por update. Não vale de muito estarmos a perder tempo a criar comandos que já foram corridos ou aqueles que servem um propósito que já foi cumprido. 

Perguntas:
Como podemos saber o propósito? 
	-> Não precisa de ser mesmo o propósito apenas precisamos de saber do que depende o output do comando. Por exemplo para o rpc enum domain groups. Apenas nos interessa o ip da máquina que foi utilizado e as credenciais. Podemos depois guardar isso num atributo da classe dos métodos e nunca mais fazemos as coisas para aquele. 

Precisamos de arranjar uma forma de:
1. Apenas correr ou contruir os comandos que ainda não construimos. Acho que isso podemos fazer a tal questão do propósito e guardar as coisas de interesse.


2. Pode haver mais que uma alteração de estados por alteração. Ou seja, quando descobrimos algo e vamos fazer o update_components, podemos alterar mais que um objeto e despoletar mais do que uma alteração de estado para cada objeto. Devemos apenas verificar os estados depois das alterações estarem todas feitas. E tentar garantir ao máximo que não estamos a verificar de forma parva, ou seja, duas alterações para o mesmo objeto apenas se deve verificar o estado uma vez e não duas.

Isto poderia ser feito noutra thread, ou na mesma, mas dava jeito que apenas fosse feito quando a alteração toda acabasse de forma a não ter duplicados. 

## Bugs fixed

## Code Implementations
Implementing the RPC group enumerations. 1 hour more or less (with the bugs)

1. Em relação a criar eventos que não deveriam ser criados duas vezes o objetivo era agora ter uma set com os argumentos que já foram usados para correr. Desta forma ele primeiro verifica se já criou eventos com aqueles argumentos, se já passa à frente.



