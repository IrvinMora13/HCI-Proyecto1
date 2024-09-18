from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from bus import event_bus
from PyQt5 import QtCore, QtGui, QtWidgets


app = FastAPI()

print(f"ID del EventBus en ventana.py: {id(event_bus)}")



html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str,ws:WebSocket = None ):
        for connection in self.active_connections:
            if(ws != connection):
                await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {message}", websocket)
            await manager.broadcast( f"Client #{client_id} says: {message}",websocket)
            event_bus.call("ws_message", client_id,  message, ui)
            event_bus.call("ws_instance", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat",websocket,)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Creacion de la ventana
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Label Name
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(0, 0, 131, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        #Input del mensaje
        self.inputField = QtWidgets.QLineEdit(self.centralwidget)
        self.inputField.setGeometry(QtCore.QRect(0, 60, 271, 31))
        self.inputField.setObjectName("inputField")

        

        # Boton de enviar
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(290, 60, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.sendMessageBus)

        # Lista de mensajes
        self.messageBox = QtWidgets.QTextEdit(self.centralwidget)
        self.messageBox.setGeometry(QtCore.QRect(420, 60, 361, 511))
        self.messageBox.setObjectName("messageBox")
        self.messageBox.setReadOnly(True)

        # Label de Chat
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(420, 40, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        # Main Windows
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Qt Chat"))
        self.pushButton.setText(_translate("MainWindow", "Enviar"))
        self.label_2.setText(_translate("MainWindow", "Chat"))

    def sendMessageBus(self):
        cliente_id = 1
        message = ""
        message = self.inputField.text()
        self.updateMessage(cliente_id, message)
        event_bus.call("qt_message", cliente_id, message, manager)
        self.inputField.clear()
        message = ""
        

    def updateMessage(self, cliente_id, message):
        self.messageBox.append(f"El cliente con id {cliente_id} dice: {message}")



if __name__ == "__main__":
    import uvicorn
    import threading
    import sys

    # Iniciar la aplicación FastAPI en un hilo separado
    def start_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    threading.Thread(target=start_fastapi).start()

    # Iniciar la GUI de PyQt5
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
