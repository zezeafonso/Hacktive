# Daily Report

## Goals
Test what we implemented yesterday.
Begin implementing the idea of the visitor set of update functions.

### updated Goals
+ Nao vamos ja implementar a parte do set visitor que depois faz o update. 
+ Ja percebemos que o problema era andarmos a colocar informacoes em sitios onde nao sao relevantes. Ha pouca ou quase nenhuma informacao que deve ser dependente. Quando encontramos algo temos de facto atualizar os componentes mais importantes. Mas verificar que comandos estas verificações alteram é quando as atualizações estão feitas. 
Vamos restruturar o codigo para termos melhor forma as coisas de cada metodo.
+ Os metodos vao receber objetos concretos que vao ter de estar especificados. Assim conseguimos saber 
+ Vamos reestrutura o codigo de modo a fazer sentido e ficar mais facil de entender. 
ja e hora para isso. Queremos implementar de forma a que consigamos correr o programa
ate colocarmos os hosts na network.
(depois fazemos o resto.)
(Ha muita coisa no codigo que possivelmente vai mudar) 

### IDEAS
[apenas precisamos de correr o update checks no fim de um filter]
quando nós encontramos algo por um filter isso muda as coisas. Há estados que vão ser alterados. Tendo em conta essas alterações novos comandos poderão ser corridos uma vez que há novas informações. 
Quando é que precisamos de averiguar estas novas situações. 
Quando um filter encontra algo, ele encontra algo relevante para uma informação que já sabíamos e com o comando desenvolve-mo-la. Ou seja, o filtro dá nos mais informação sobre uma coisa que já temos, e todas as informações que nos dá é sobre informação que ou já temos ou informação aprofundada do filtro sobre a informação que ele já deu anteriormente. 
Dessa forma nunca precisamos de ver alterações do estado duranto as atualizações de um filtro e apenas após.

Nós de facto para os novos métodos, ou os métodos que vamos correr na verdade só queremos saber das alterações que aconteceram. Não estamos muito interessados em voltar a correr comandos que já tínhamos corrido ou coisas do género, por isso se calhar investíamos no facto de ver as alterações ao estado e apenas usar essas para correr o bicho.

Um dos problemas que me está a chatear é o das dependências de informação e a propagação de estados. 
O problema é: as funções de check_updates vão sendo adicionadas e no fim são chamadas pela ordem em qeu são adicionadas.
Ou seja, se não houver uma ordem pela qual são adicionadas, vai acontecer chamar-mos o check updates para um objeto filho e depois chamarmos para um objeto pai. Isto porque a informação pertence aos objetos e não é global, mas poderia ser global. 

[Pode ser uma boa idea]
Se a informação fosse global, até poderíamos associar pedaços da informação aos objetos. E a informação poderia ser relevante para mais do que um. Dessa forma depois essa informação era passada diretamente para os objetos em vez de ser privada ou apenas para um e depois ter que ser passada de um lado para o outro. 

[Acho que podemos implementar]
Há informação que é constante por exemplo. O ip do MSRPC server, ldap server etc. Essa informação podia ficar como constante ou atributo do objeto mas o resto da informação aquela que varia com os updates não ficava como atributo. Porque de certa forma não pertence apenas aquele bartoleiro.
Ou é global ao programa todo ou fica guardado num objeto qualquer.


[INFORMACAO]
A informação não está no sítio correto e é por isso que andamos com depêndencias de informação. A parte do domínio é apenas referente ao domínio (objeto) o MS-RPC e o LDAP não tem nada a ver com esta informação.

Os métodos de informação do domínio poderão usar métodos do MS-RPC, do LDAP, do SMB. Mas são métodos apenas do domínio que chamam esses do (MS-RPC/LDAP/SMB).
Não há muita partilha de informação.

No máximo pode haver alguma partilha entre hosts que pertencem ao domínio e o domínio em si. Por exemplo saber se há um novo MS-RPC. 
Mas acho que o melhor até seria no update components nós colocarmos logo uma referência a esse MR-RPC server. 

### IDEAS for tommorrow

## Work
The testing is now concluded. We are testing the correct way if the args were already used for a method. 
Now we should be concerned with improving the speed and behaviour of the program we're wasting a lot of time, for each thing a filtered object finds. Maybe we can just update the other objects whenever we finish all the things a filter found.

