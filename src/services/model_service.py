from src.models.llm_model_class import LLMModel, TokenStreamer
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


class LLMEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5


def request_ids_to_cache_id(request_ids):
    sorted_ids = sorted(request_ids)
    return ''.join(sorted_ids)


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
        if event.execution_id in event_queues:
            event_queues[event.execution_id].put(event)


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        response_queue.put({
            "type": LLMEventTypes.START,
            "execution_id": request["execution_id"],
            "request_ids": request["request_ids"]
        }),

        stream = TokenStreamer(
            lambda values: response_queue.put({
                "request_ids": request["request_ids"],
                "execution_id": request["execution_id"],
                "type": LLMEventTypes.INITIALIZED,
                "tokens": values
            }),
            lambda values: response_queue.put({
                "request_ids": request["request_ids"],
                "execution_id": request["execution_id"],
                "type": LLMEventTypes.PROGRESS,
                "tokens": values
            })
        )

        sequences, past_key_values = llm_model.generate_cache(
            request["tokens"],
            request["masks"],
            request.get("values", None),
            request["config"],
            stream
        )

        response_queue.put({
            "request_ids": request["request_ids"],
            "execution_id": request["execution_id"],
            "type": LLMEventTypes.COMPLETE,
            "sequences": sequences,
            "values": past_key_values
        }),


def prepare_prompts(prompts):
    global llm_model
    tokens, masks = llm_model.tokenize_prompts(prompts)
    values = None
    return {tokens, masks, values}


def add_prompts_execution(request_ids, prompts, request_config):
    global cache
    cache_id = request_ids_to_cache_id(request_ids)
    execution_id = uuid.uuid4()
    target = cache[cache_id] if cache_id in cache else prepare_prompts(prompts)

    event_queues[execution_id] = queue.Queue()
    execution_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "tokens": target.tokens,
        "masks": target.masks,
        "values": target.values,
        "config": request_config
    })

    return event_queues[execution_id]
