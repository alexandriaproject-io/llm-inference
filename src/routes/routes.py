from src.controllers import ws_controller, generate_controller
from aiohttp import web


def set_routes(app):
    app.add_routes([
        web.post('/api/generate-one', generate_controller.generate_one),
        web.post('/api/generate-batch', generate_controller.generate_batch),
        web.get('/api/ws', ws_controller.websocket_handler),
    ])
    return
