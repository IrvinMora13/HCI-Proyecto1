# HCI Proyecto1
## Funcionamiento

Tenemos dos archivos **bus.py** y **fast.py** en donde el archivo a iniciar o correr es **fast.py** 

En el main tenemos dos hilos el de uvicorn que ejecuta el servidor de fastApi y el hilo principal que se encarga de la ejecucion de PyQt 5 para la interfaz grafica.

En el webSocket al momento de mandar un mensaje por en la logistica tenemos un eventBus en el cual invoca la funcion de ws_message en donde enviamos parametros como el client_id y el mensaje ademas de la UI de pyQt de  de esta forma guardamos  el mensaje en el eventBus y solamente invocamos un metodo de la clase  de la UI para que se actualice la interfaz grafica con el mensaje enviado con su ID.

En la  UI tenemos un evento que se activa cada vez que se envia un mensaje en el eventBus llamdo qt_message con los parametros de cliente_id, message y manager  que es la clase del WebSocket en donde con manager invocamos el metodo de broadcast para enviar el mensaje a todo el mundo de los usuarios de WebSocket
