# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un ejemplo de cliente-servidor el cual corre en containers con la ayuda de [docker-compose](https://docs.docker.com/compose/). El mismo es un ejemplo práctico brindado por la cátedra para que los alumnos tengan un esqueleto básico de cómo armar un proyecto de cero en donde todas las dependencias del mismo se encuentren encapsuladas en containers. El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers.

Por otro lado, se presenta una guía de ejercicios que los alumnos deberán resolver teniendo en cuenta las consideraciones generales descriptas al pie de este archivo.

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que posee encapsulado diferentes comandos utilizados recurrentemente en el proyecto en forma de targets. Los targets se ejecutan mediante la invocación de:

* **make \<target\>**:
Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de _debugging_ y _troubleshooting_.

Los targets disponibles son:
* **docker-compose-up**: Inicializa el ambiente de desarrollo (buildear docker images del servidor y cliente, inicializar la red a utilizar por docker, etc.) y arranca los containers de las aplicaciones que componen el proyecto.
* **docker-compose-down**: Realiza un `docker-compose stop` para detener los containers asociados al compose y luego realiza un `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene.
* **docker-compose-logs**: Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose.
* **docker-image**: Buildea las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para testear nuevos cambios en las imágenes antes de arrancar el proyecto.
* **build**: Compila la aplicación cliente para ejecución en el _host_ en lugar de en docker. La compilación de esta forma es mucho más rápida pero requiere tener el entorno de Golang instalado en la máquina _host_.

### Servidor
El servidor del presente ejemplo es un EchoServer: los mensajes recibidos por el cliente son devueltos inmediatamente. El servidor actual funciona de la siguiente forma:
1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor procede a recibir una conexión nuevamente.

### Cliente
El cliente del presente ejemplo se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma.
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
recibe mensaje del cliente y procede a responder el mismo.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
Servidor desconecta al cliente.
4. Cliente vuelve al paso 2.

Al ejecutar el comando `make docker-compose-up` para comenzar la ejecución del ejemplo y luego el comando `make docker-compose-logs`, se observan los siguientes logs:

```
$ make docker-compose-logs
docker compose -f docker-compose-dev.yaml logs -f
client1  | time="2023-03-17 04:36:59" level=info msg="action: config | result: success | client_id: 1 | server_address: server:12345 | loop_lapse: 20s | loop_period: 5s | log_level: DEBUG"
client1  | time="2023-03-17 04:36:59" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1\n"
server   | 2023-03-17 04:36:59 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: in_progress
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:36:59 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: in_progress
server   | 2023-03-17 04:37:04 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:04 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2023-03-17 04:37:04 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:04" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2\n"
server   | 2023-03-17 04:37:09 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:09 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
server   | 2023-03-17 04:37:09 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:09" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3\n"
server   | 2023-03-17 04:37:14 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:14 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
client1  | time="2023-03-17 04:37:14" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4\n"
server   | 2023-03-17 04:37:14 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:19" level=info msg="action: timeout_detected | result: success | client_id: 1"
client1  | time="2023-03-17 04:37:19" level=info msg="action: loop_finished | result: success | client_id: 1"
client1 exited with code 0
```

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Modificar la definición del DockerCompose para agregar un nuevo cliente al proyecto.

### Resolucion ejercicio N°1.1:
Se utilizo python para crear un archivo llamado "create_new_docker_compose.py" el cual crea una cantidad N de clientes. El mismo debe ser ejecutado de la siguinete manera:
`py .\create_new_docker_compose N` con N la cantidad de clientes deseada.

### Resolucion Ejercicio N°2:
Se agrega al archivo docker-compose-dev los volumenes para el server y de los clientes, con el fin de vincular los archivos de la maquina host con los archivos del container. Siendo estos archivos `config.ini` para el server y `config.yaml` para el cliente. En la declaracion del volumen unicamente se comparten dichos archivos, es decir, no se comparte toda la carpeta. Asi mismo, se aclara que se opto por volumenes sin nombre o tambien llamados anonimos.

Paralelamente, se modifica el script creado en el ejercicio 1.1 con el fin de añadir los volumenes.

Se verifica el correcto funcionamiento al realizar 'make docker-compose-up' con 'docker-image' comentado y corroborando los cambios realizados en la configuracion del servidor y de los clientes sin necesidad de realizar un nuevo build de las imagenes.

### Resolucion ejercicio N°3:

Ejecutar `./server_validation.sh`.

El script `server_validation.sh` se encarga de levantar los containers del server y del cliente de prueba junto a la network que los conecta. Una vez iniciados ambos containers, se instala netcat en el cliente de prueba y tras ello se ejecuta en la bash del container el siguiente comando:  
`if [ "$(echo "Test01" | nc server 12345)" = "Test01" ]; then echo "OK"; else echo "Error"; fi`

Este comando muestra `OK` por la terminal en caso de exito o `Error` en caso de error. El funcionamiento del comando se basa en una estrucuta if, donde la condicion de verdad es la igualdad del resultado esperado (Test01) al ejecutar el comando nc server 12345 con 'Test01' como entrada.

Continuando con `$(echo "Test01" | nc server 12345)`, aqui capturamos el resultado de la ejecucion de las instrucciones entre parentesis. Se envia por stdin "Test01" al comando "nc server 12345" para enviar el mensaje "Test01" a la IP "server" (configurada en el archivo config.ini del server) en el puerto 12345.

Por ultimo, se detienen y eliminan los containers utilizados para la prueba.

### Resolucion ejercicio N°4:
Se agregan los handlers respectivos para el servidor y para el cliente para lograr obtener un graceful finish en caso de recibir una señal SIGTERM.

En caso del servidor, se utiliza la libreria signal. Dicha libreria nos permite definir un handler que sera llamado al momento de recibir la señal SIGTERM, este handler cambia el estado de una variable interna de server. En el bucle principal del servidor se verifica el estado de dicha variable para salir del bucle en caso que corresponda. Tras esto, se cierran los recursos abiertos por el programa y se finaliza la ejecucion.

En el caso del cliente, se utilizan las librerias `os` y `syscall`. Previo al loop del cliente, se llama asincronicamente al handler de la señal, dicha señal proviene de un channel por lo que el handler al recibir dicho valor por el channel envia el valor true por un channel llamado "finish channel". Este segundo channel es escuchado por el loop principal mediante un select, lo que permite que al momento en el que se reciba el valor true por dicho canal se salga del loop cerrando correctamente los recursos del cliente.

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base al código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Resolucion ejercicio N°5:

#### Cliente
El cliente recibe como variables de entorno todos los datos necesarios para realizar una apuesta. Dicha informacion se guarda dentro de la configuracion que se encuentra dentro del propio cliente.

Se agrega un el archivo `bet.go` donde se declara el tipo `BetRegister` junto a sus correspondientes funciones. Al momento de realizar una apuesta, el cliente utiliza la funcion `sendBetMessage` donde se crea una apuesta a partir de los datos cargados en la configuracion y luego se emplea dicha apuesta para crear un mensaje segun el protocolo descipto mas adelante y se envia hacia el servidor con la funcion `sendMessage`. Esta ultima funcion es la encargada de enviar los datos hacia el servidor evitando el fenomeno de short-write.

Tras enviar la apuesta al servidor, el cliente utiliza la funcion `receiveMessage` para recibir el ACK por parte del servidor. En este caso, la funcion esta preparada para evitar el fenomeno de short-read.

#### Servidor
Se agrega la funcion `_receive_message` la cual devuelve el mensaje leido desde el socket evitando el fenomeno de short-read. Tras ello, se utiliza la funcion `procces_message` para crear una apuesta desde el mensaje obtenido y luego almacenarla.

Por ultimo, se envia al cliente un ACK mediante la funcion `_send_ack_message` la cual evita el problema de short.write.

#### Protocolo de Comunicación:
En lo que respecta al protocolo de comunicacion planteado para la resolucion del trabajo practico, consiste en una estructura de mensaje que se compone de un header y un payload.

En primer lugar en el header, unicamente tendremos el tamaño del payload. Este header se encuentra al inicio del mensaje y al igual que el resto de componentes se encuentra separador del mensaje por una coma. El header del mensaje se considera el tamaño minimo a leer del mensaje y en caso de que la lectura del mensaje no contenga al menos al header completo se debera enviar nuevamente.

Por otro lado, el payload contendra todos los campos correspondientes para el contenido del mensaje. En caso de ser un mensaje de apuesta, se compondra de los campos necesarios para realizar la apuesta con sus campos separados por una coma. Por otro lado, en caso de ser un mensaje de ACK se tendra la cadena "ACK" y el tamaño del paquete recibido anteriormente.


Ejemplo de mensaje de apuesta: payload_size,agency_id,name,lastname,document,birthdate,number

Ejemplo de mensaje ACK: payload_size,ACK:size_of_received_message


Simplemente a modo de aclaracion, se menciona que como convencion se opto por que en caso de que se detecte un error al enviar o recibir un mensjae, no se reenviara el mensaje. Por ejemplo, en caso de que al momento de enviar la apuesta, la funcion `Write` del socket falle, no se reenviara la apuesta.  
En lo que respecta a la eleccion del protocolo, es importante destacar que si bien es muy simple de parsear gracias a los separadores, no es el mas eficiente. Esto ya que se podria haber optado por un protocolo con campos de tamaño fijo y campos de tamaño variable cuyos tamaños se prodrian agregar en el header (el cual nuevamente seria de un tamaño fijo). De esta forma se evita el envio de separadores y se realiza una mejor administracion de los recursos de la red. El motivo por el cual no se opto por esta ultima opcion fue simplemente el tiempo requerido para realizarlo.  

#### Aclaracion importante respecto al protocolo:
Existe una diferencia entre la implementacion del protoclo para el cliente y para el servidor. Esta consiste en el modo de lectura de un mensaje entrante, el servidor lo realiza de forma "correcta" es decir lee la informacion del socket hasta encontrar el separador del header y luego lee el tamaño que contenia dicho header. Sin embargo, el cliente lee una linea completa el socket.  
Esta diferencia se basa en que mi implementacion es compatible con este modo de lectura ya que no se envia mas de un mensaje a la vez por parte del servidor. Soy conciente de que no es algo "prolijo" pero se realizo en pos de ahorrar tiempo y continuar con el resto de ejercicios ya que por la forma en la que se comunican en mi TP no traeria problemas. Esta claro que en caso de querer formalizar el protocolo se realizaria una correcta implementacion como la que posee el servidor. 

#### Ejecucion del ejercicio 5:
Se debe ejecutar `make docker-compose-up` para levantar los containers (5 clientes y 1 servidor) y luego ejecutar `make docker-compose-logs`. Por ultimo, para finalizar la ejecucion se debe utilizar el comando `make docker-compose-down` para terminar de forma graceful con todos los containers.

### Resolucion ejercicio N°6:

#### Cantidad de apuestas por chunk
En primer lugar, para calcular la cantidad de apuestas que es posible enviar en un chunk para no exceder los 8kB se toma al peor caso (apuesta mas larga) como cota de longitud y para ello se toman los siguientes parametros:

- agency_id: Dado el alcance del trabajo practico, se toma como maximo cuatro digitos (4 bytes).
- name: Se toma como longitud maxima 30 caracteres (Dado que un caracter especial puede ocupar hasta 4 bytes se destinan 120bytes para este campo).
- lastname: Se utiliza una longitud maxima de 30 caracteres (Dado que un caracter especial puede ocupar hasta 4 bytes se destinan 120bytes para este campo).
- document: Entero de 8 digitos (8 bytes).
- birthdate: Longitud maxima de 10 caracteres (10 bytes.)
- number: Se asume que el numero maximo es 9999 por lo que es un entero de 4 digitos (4 bytes).

Por lo tanto, al sumarle los separadores (',') y el tamaño del header (numero entero de 3 digitos) el mensaje mas largo posible seria de aproximadamente de 280 bytes.


280 bytes > MAX_LEN_AGENCY + MAX_LEN_NAME + MAX_LEN_LASTNAME + MAX_LEN_DOCUMENT + MAX_LEN_BIRTHDATE + MAX_LEN_NUMBER + LEN_ADD_BY_PROTOCOL + LEN_MAX_HEADER

280bytes > 4bytes + 120bytes + 120bytes + 8bytes + 10bytes + 4bytes + 7bytes + 4bytes

Si tomamos 280bytes como cota para la cantidad de apuestas que se pueden realizar en un chunk, entonces podriamos realizar hasta un maximo de 27 apuestas por chunk. Nuevamente, se hace mencion al apartado del punto 5 donde se plantea que es posible reducir el tamaño de los mensajes mediante la modificacion del protocolo.

En lo que respecta a las constantes como la cantidad de apuestas por chunks o el path del archivo el cual deberan utilizar los clientes, se añadieron en el archivo de configuracion llamado config.yaml. Se hace especial mencion a la modificacion del loop lapse aumentando su valor para asegurar que todas las apuestas lleguen al servidor.

#### Modificaciones al protocolo de comunicacion

Adicionalmente, se menciona que se modifico el protocolo de comunicacion levemente para poder adaptarlo a este ejercicio. Aqui se agrego un nuevo mensaje de cuyo payload es 'FIN' con el objetivo de avisarle al servidor que se finalizo el envio de datos por lo que el servidor puede enviarle el ACK del chunk completo. Este ACK tambien fue modificado y ahora envia la cantidad de paquetes que se procesaron en el chunk. Cabe aclara que a medida que los paquetes le llegan al servidor, el mismo los va procesando y no espera a tener todo el chunk completo para inciar el procesamiento para evitar tener cargados en memoria todos esos datos en caso de utilizar chunks muy grandes.  

#### Ejecucion del ejercicio 6:
Al igual que el ejercicio 5 se deben utilizar los comandos `make docker-compose-up` para levantar los containers (5 clientes y 1 servidor), `make docker-compose-logs` y `make docker-compose-down` para terminar de forma graceful con todos los containers.

### Resolucion ejercicio N°7:

Para la resolucion de este ejercicio se modifica levemente el protocolo añadiendo un nuevo tipo de mensaje. Este tipo de mensaje es READY y es enviado por el cliente cuando finaliza el envio de todos los chunks. De esta forma, se tiene un mensaje de FIN para el caso donde se termina de enviar un chunk del archivo y un mensaje READY para cuando se termino de enviar el ultimo chunk. Es importante aclarar que al enviar el ultimo chunk, unicmanete se envia el mensaje READY, es decir, no se enviara el mensaje FIN.

Se barajo la posibilidad de utilizar un flag e incluirlo en el header, el cual adopte un valor al momento de que el cliente se encuentra en estado ready, sin embargo por motivos de tiempo y facilidad de implementacion respecto al protocolo existente se opto por un mensaje especial.


Pasando al funcionamiento de parte del cliente, al finalizar el envio de todas las apuestas se queda a la espera de los ganadores. Estos llegaran como con el dato del DNI en el payload del mensaje, de esta forma el cliente lee el mensaje y agrega el DNI a la lista de ganadores. Cuando se detecte que el servidor cerro el canal de comunicaciones, se asume que no hay mas ganadores.


Desde el punto de vista del servidor, se añade el soporte para el nuevo tipo de mensaje (READY). Cuando se detecta este mensaje, se guarda el socket en un diccionario llamado `_ready_clients` cuyas claves son los ID de los clientes y los valores sus respectivos sockes. Simplemente a modo de aclaracion, se penso en cerrar la conexion y que luego el servidor inicie una conexion con el cliente, sin embargo, no consideraba que sea correcto que el servidor inicie la conexion.
El servidor cuenta con una constante con la cantidad total de clientes, por lo tanto cuando se detecta que el tamaño del diccionario es igual a la cantidad de dicha constante, se utiliza la funcion `_send_winners` la cual utiliza filter junto a la funcion `load_bets` y `has_won` para iterar sobre los bets del archivo (evitando cargarlos todos en memoria simultaneamente) y luego se envia el documento a cada cliente segun el ID guardado en la bet empleando el diccionario anteriormente mecionado. Al enviar todos los ganadores, se cierran todos los sockets.


#### Ejecucion del ejercicio 7:
Se ejecuta de la misma manera que el ejercicio 6.

## Parte 3: Repaso de Concurrencia

### Resolucion ejercicio N°8:

Dado que en este ejercicio el servidor atiende a los clientes de forma concurrente, no es necesario finalizar las conexiones de los clientes. De esta manera, se modifica al cliente para no cerrar la conexion.  
#### Funcionamiento del proceso padre del servidor:
En lo que respecta a las modificaciones en el servidor, se agrega el objeto `ProcessManager` el cual es la abstraccion encargada de un proceso hijo del server. El proceso padre quedara a la espera de conexiones y cuando llegue una conexion crea una instancia de ProcessManager que contiene el pipe por el que se va a comunicar con el proceso hijo junto al socket de dicho cliente y el id.  
Este ultimo atributo, se inicializa en un valor invalido (`0`) ya que debera ser cargado por el propio hijo durante su ejecucion.  
Cuando el servidor cree una cantidad de `TOTAL_AMOUNT_OF_CLIENTS` de instancias de ProcessManager significa que todos los clientes estan conectados por lo que se procede a cargarles el ID correcto a cada ProcessManager. Como explicare mas adelante, este proceso tiene dos finalizades siendo el primero el asignarle un cliente especifico a un ProcessManager y de esta forma unicamente mandarle los ganadores correspondientes a dicha agencia. La segunda funcionalidad que tiene el hecho de configurar el ID es avisar al proceso padre que el cliente finalizo de enviar las apuestas.  
De esta forma, cuando se configuran los ID en ProcessManager el proceso padre tiene la certeza de que puede realizar la loteria ya que no queda ninguna apuesta sin registrar. Otra posible solucion, seria en lugar de mandar el ID, que el proceso hijo le mande un bool cuando este listo para realizar la loteria aunque luego el proceso padre le deberia enviar a todos los hijos todos los ganadores y seria responsabilidad de ellos tomar unicamente los que necesitan. Por ultimo, se menciona que seria posible definir un protocolo mas complejo para el intercambio de informacion entre el padre y el hijo que logre el mismo resultado de manera mas clara sin embargo por motivos de tiempo se opto por la convencion anteriormente mencionada.  
Continuando con la logica del padre, cuando todos los ProcessManager tienen sus ID cargados se procede a la obtencion de los ganadores y luego al envio de los ganadores a los respectivos hijos. Tras ello, se realiza un graceful finish de los procesos hijos y se eliminan de la lista de procesos permitiendo al servidor continuar con el loop de aceptacion de clientes.  
Cabe aclarar que toda la comunicacion entre el proceso padre e hijo se realiza utilizando un `Pipe` bidireccional.  
 
#### Funcionamiento del proceso hijo del servidor:

Como se menciono anteriormente, una vez creado el hijo el mismo permanece conectado al socket del cliente hasta el final de la comunicacion (donde le envia los ganadores). De esta forma, el proceso hijo quedara en un loop en el cual reciba las apuestas del cliente y en el momento en el que se finalize con la recepcion del total de las apuestas del cliente, se enviara al padre el ID del cliente que esta atendiendo.  
Tras enviarle el ID del su cliente al padre el proceso queda a la espera de los ganadores que leera del propio Pipe que lo conecta con el proceso padre. Cuando se terminen de recibir todos los ganadores, se procede a enviarlos hacia el cliente y finalizar su ciclo de vida permitiendo que el proceso padre le pueda realizar un `join()`.  
En lo que respecta al acceso del archivo de bets.csv, se utiliza un lock para garantizar que unicamente un proceso pueda acceder al mismo y de esta forma todos los proceso hijos pueden recibir apuestas que las almacenaran cuando obtengan el lock.