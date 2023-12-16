from src.models.llm_model_class import LLMModel, BaseStreamer
from src.config import config
import queue
import threading
import enum
import uuid
from cachetools import TTLCache

llm_model: LLMModel
execution_queue = queue.Queue()
response_queue = queue.Queue()
event_queues = {}
cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)


def do_stuff():
    return "ok"


class LLMEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5


class LLMInternalEventTypes(enum.Enum):
    START = 1
    PROGRESS = 4
    COMPLETE = 5


def request_ids_to_cache_id(request_ids):
    sorted_ids = sorted(request_ids)
    return ''.join(sorted_ids)


def progress_put_in_queue(request_ids, execution_id, values):
    global response_queue
    response_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.PROGRESS,
        "tokens": values
    })


def start_put_in_queue(request_ids, execution_id):
    global response_queue
    response_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.START,
    })


def complete_put_in_queue(request_ids, execution_id, sequences, past_key_values):
    global response_queue
    response_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.COMPLETE,
        "sequences": sequences,
        "values": past_key_values
    })


def init_llm_model():
    global llm_model
    llm_model = LLMModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
    llm_model.load_model()
    llm_model.run_model()

    threading.Thread(target=handle_model_generation, daemon=True).start()
    threading.Thread(target=handle_model_responses, daemon=True).start()

    return llm_model


def handle_model_responses():
    global cache
    while True:
        event = response_queue.get()
        if event is None:  # Use None as a signal to stop the thread
            break
        if event["execution_id"] in event_queues:
            event_queues[event["execution_id"]].put(event)


class ResponseStreamer(BaseStreamer):
    def __init__(self, request_ids, execution_id):
        self.request_ids = request_ids
        self.execution_id = execution_id

    def put(self, value):
        progress_put_in_queue(self.request_ids, self.execution_id, value)

    def end(self):
        return


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        start_put_in_queue(request["request_ids"], request["execution_id"])
        stream = ResponseStreamer(request["request_ids"], request["execution_id"])

        sequences, past_key_values = llm_model.generate_cache(
            request["tokens"],
            request["masks"],
            request.get("values", None),
            request["config"],
            stream
        )

        complete_put_in_queue(request["request_ids"], request["execution_id"], sequences, past_key_values)


def prepare_prompts(prompts):
    global llm_model
    tokens, masks = llm_model.tokenize_prompts(prompts)
    return {
        "tokens": tokens,
        "masks": masks,
        "values": None
    }


def add_prompts_execution(request_ids, prompts, request_config):
    global cache
    cache_id = request_ids_to_cache_id(request_ids)
    execution_id = uuid.uuid4()
    target = cache[cache_id] if cache_id in cache else prepare_prompts(prompts)

    event_queues[execution_id] = queue.Queue()
    execution_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "tokens": target["tokens"],
        "masks": target["masks"],
        "values": target["values"],
        "config": request_config
    })

    return event_queues[execution_id]