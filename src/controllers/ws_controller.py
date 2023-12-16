from aiohttp import web

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str("Message received: " + msg.data)
        elif msg.type == web.WSMsgType.ERROR:
            print('WebSocket connection closed with exception %s' % ws.exception())

    print('WebSocket connection closed')
    return ws