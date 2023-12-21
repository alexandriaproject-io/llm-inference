from aiohttp import web
from src.routes.routes import set_routes
import src.services.model_service as model_service
import aiohttp_swagger
from src.config import config

if __name__ == '__main__':
    model_service.init_llm_model()

    app = web.Application()
    set_routes(app)

    aiohttp_swagger.setup_swagger(
        app,
        swagger_url="/swagger",
        title="API documentation",
        description=f"You can find UI demos at http://localhost:{config.SERVER_PORT}/ui"
    )
    web.run_app(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
