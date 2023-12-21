from aiohttp import web
from src.routes.routes import set_routes, set_cors, set_ui
import src.services.model_service as model_service
import aiohttp_swagger
from src.config import config

if __name__ == '__main__':
    model_service.init_llm_model()
    app = web.Application()
    set_routes(app)
    aiohttp_swagger.setup_swagger(
        app,
        ui_version=3,
        swagger_url="/swagger",
        title="API documentation",
        description=f"<h2>You can find UI demos at <a target='_blank' style=\"font-size:0.9em\" href='/ui/'>http://localhost:{config.SERVER_PORT}/ui</a></h2>",
    )
    set_ui(app)
    set_cors(app)

    web.run_app(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
