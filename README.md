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

En primer lugar al header, unicamente tendremos el tamaño del payload. Este header se encuentra al inicio del mensaje y al igual que el resto de componentes se encuentra separador del mensaje por una coma. El header del mensaje se considera el tamaño minimo a leer del mensaje y en caso de que la lectura del mensaje no contenga al menos al header completo se debera enviar nuevamente.

Por otro lado, el payload contendra todos los campos correspondientes para el contenido del mensaje. En caso de ser un mensaje de apuesta, se compondra de los campos necesarios para realizar la apuesta con sus campos separados por una coma. Por otro lado, en caso de ser un mensaje de ACK se tendra la cadena "ACK" y el tamaño del paquete recibido anteriormente.


Ejemplo de mensaje de apuesta: payload_size,agency_id,name,lastname,document,birthdate,number

Ejemplo de mensaje ACK: payload_size,ACK:size_of_received_message


Simplemente a modo de aclaracion, se menciona que como convencion se opto por que en caso de que se detecte un error al enviar o recibir un mensjae, no se reenviara el mensaje. Por ejemplo, en caso de que al momento de enviar la apuesta, la funcion `Write` del socket falle, no se reenviara la apuesta.

### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento. La cantidad de apuestas dentro de cada _batch_ debe ser configurable. Realizar una implementación genérica, pero elegir un valor por defecto de modo tal que los paquetes no excedan los 8kB. El servidor, por otro lado, deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:
Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo, no podrá responder consultas por la lista de ganadores.
Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

## Parte 3: Repaso de Concurrencia

### Ejercicio N°8:
Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo.
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

En caso de que el alumno implemente el servidor Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Consideraciones Generales
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios.
El _fork_ deberá contar con una sección de README que indique como ejecutar cada ejercicio.
La Parte 2 requiere una sección donde se explique el protocolo de comunicación implementado.
La Parte 3 requiere una sección que expliquen los mecanismos de sincronización utilizados.

Finalmente, se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección provistos [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).
