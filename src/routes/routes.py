from src.controllers import ws_controller, generate_controller
from aiohttp import web
import asyncio

async def handle(request):
    response = web.StreamResponse(headers={'Transfer-Encoding': 'chunked'})
    await response.prepare(request)

    for i in range(100):

        chunk = f"Chunk {i}\n"
        await response.write(chunk.encode('utf-8'))

        await asyncio.sleep(0.1)


    await response.write_eof()
    return response


def set_routes(app):
    app.add_routes([
        web.post('/api/generate-one', generate_controller.generate_one),
        web.post('/api/generate-batch', generate_controller.generate_batch),
        web.get('/api/ws', ws_controller.websocket_handler),
        web.get('/test', handle)

    ])
    return
