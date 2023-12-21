from src.controllers import ws_controller, generate_controller
from aiohttp import web
import aiohttp_cors


async def index(request):
    return web.FileResponse('ui-app/build/index.html')


def set_routes(app):
    cors = aiohttp_cors.setup(app)

    app.add_routes([
        # Static UI hosting
        web.get('/ui', index),
        web.get('/ui/{tail:[^\.]*}', index),
        web.static('/ui/', path='ui-app/build', name='static'),
        # HTTP endpoints and Web Socket
        web.post('/api/generate-one', generate_controller.generate_one),
        web.post('/api/generate-batch', generate_controller.generate_batch),
        web.get('/api/ws', ws_controller.websocket_handler),
    ])

    for route in list(app.router.routes()):
        cors.add(route, {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
    return
