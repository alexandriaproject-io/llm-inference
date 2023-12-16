from aiohttp import web
from routes.routes import set_routes
from services.model_service import init_llm_model
import aiohttp_swagger

if __name__ == '__main__':
    init_llm_model()

    app = web.Application()
    set_routes(app)

    aiohttp_swagger.setup_swagger(app, swagger_url="/swagger", title="API documentation")
    web.run_app(app, port=8080)
