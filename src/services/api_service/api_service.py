import uuid
import aiohttp
import aiohttp_swagger
import asyncio
from aiohttp import web
from src.config import config
from src.routes.routes import set_routes, set_cors, set_ui
from src.models.huggingface.llm_tokenizer import LLMTokenizer
from src.models.llama_cpp.LLMCPP_tokenizer import LLMCPPTokenizer
from src.services.api_service.utils import ResponseHandler, AsyncQueueHandler, ExecutionHandler


@web.middleware
async def extend_request(request, handler):
    setattr(request, 'executions', ExecutionHandler(request.app))
    return await handler(request)


def start_server(execution_queue, events_queue):
    app = web.Application(middlewares=[extend_request])

    if not config.USE_LLAMA_CPP:
        app["tokenizer"] = LLMTokenizer(config.MODEL_PATH, {"SPACE_TOKEN_CHAR": config.SPACE_TOKEN_CHAR})
    else:
        app["tokenizer"] = LLMCPPTokenizer()
    async def on_startup(t_app):
        t_app["execution_queue"] = AsyncQueueHandler(execution_queue)
        t_app["events_queue"] = AsyncQueueHandler(events_queue)
        t_app["response_events"] = ResponseHandler(t_app["events_queue"], t_app["tokenizer"])
        asyncio.create_task(t_app["response_events"].listen())

    app.on_startup.append(on_startup)

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
    aiohttp.web.run_app(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
