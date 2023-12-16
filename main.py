from aiohttp import web
from src.routes.routes import set_routes
import src.services.model_service as model_service
import aiohttp_swagger

if __name__ == '__main__':
    model_service.init_llm_model()

    app = web.Application()
    set_routes(app)

    aiohttp_swagger.setup_swagger(app, swagger_url="/swagger", title="API documentation")
    web.run_app(app, port=8080)