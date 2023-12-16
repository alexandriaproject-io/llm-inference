from ..controllers import ws_controller, generate_controller

def set_routes(app):
    app.router.add_get('/api/generate-one', generate_controller.generate_one)
    app.router.add_get('/api/generate-one', generate_controller.generate_batch)
    app.router.add_get('/ws', ws_controller.websocket_handler)
    return
