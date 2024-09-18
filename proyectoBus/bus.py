from python_event_bus import EventBus

import asyncio

event_bus = EventBus()
websocket_instance = None

@event_bus.on("ws_message")
def fastapi_message(client_id, message, ui):
    ui.updateMessage(client_id, message)

@event_bus.on("qt_message")
def qt_message(client_id, message, qt):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(qt_message_async(client_id, message, qt))
    

async def qt_message_async(client_id, message, qt):
    global websocket_instance
    await qt.broadcast(f"Cliente #{client_id} dice: {message}")

@event_bus.on("ws_instance")
def call(websocket):
    global websocket_instance
    websocket_instance = websocket

