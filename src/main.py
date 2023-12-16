from aiohttp import web, aiohttp_swagger
from routes.routes import set_routes
from services.model_service import init_llm_model

if __name__ == '__main__':
    init_llm_model()
    app = web.Application()
    set_routes(app)

    aiohttp_swagger.setup_swagger(app, swagger_url="/api/doc", title="API documentation")
    web.run_app(app, port=8080)
