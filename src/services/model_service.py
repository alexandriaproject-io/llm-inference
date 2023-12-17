from src.models.llm_model_class import LLMModel, BaseStreamer
from src.config import config
import queue
import threading
import enum
import uuid
from cachetools import TTLCache


class LLMEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5


class LLMInternalEventTypes(enum.Enum):
    START = 1
    PROGRESS = 4
    COMPLETE = 5


llm_model: LLMModel
execution_queue = queue.Queue()
response_queue = queue.Queue()
event_queues = {}
cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)


class ResponseStreamer(BaseStreamer):
    def __init__(self, request_ids, execution_id):
        self.request_ids = request_ids
        self.execution_id = execution_id

    def put(self, value):
        progress_put_in_queue(self.request_ids, self.execution_id, value)

    def end(self):
        return


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


def complete_put_in_queue(request_ids, execution_id, sequences, past_key_values, request_config):
    global response_queue
    response_queue.put({
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.COMPLETE,
        "config": request_config,
        "sequences": sequences,
        "values": past_key_values,
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
    global event_queues
    global llm_model
    while True:
        event = response_queue.get()
        if event is None:  # Use None as a signal to stop the thread
            break
        if not event["execution_id"] in event_queues:
            continue;

        cache_id = request_ids_to_cache_id(event["request_ids"])
        cached_item = cache[cache_id] if cache_id in cache else {}

        # handle start events for batch
        if event["type"] == LLMInternalEventTypes.START:
            for request_id in event["request_ids"]:
                event_queues[event["execution_id"]].put({
                    "request_id": request_id,
                    "type": LLMEventTypes.START
                })
        # handle progress events for batch
        elif event["type"] == LLMInternalEventTypes.PROGRESS:
            # Determine event sub type
            event_type = LLMEventTypes.INITIALIZED if event["tokens"].dim() == 2 else LLMEventTypes.PROGRESS

            for request_id, tokens in zip(event["request_ids"], event["tokens"]):
                event_queues[event["execution_id"]].put({
                    "request_id": request_id,
                    "type": event_type,
                    "text": llm_model.decode_output(tokens)
                })


        # handle complete events for batch
        elif event["type"] == LLMInternalEventTypes.COMPLETE:
            for request_id, sequence in zip(event["request_ids"], event["sequences"]):
                event_queues[event["execution_id"]].put({
                    "request_id": request_id,
                    "type": LLMEventTypes.COMPLETE,
                    "text": llm_model.decode_output(sequence)
                })

        # cache[cache_id] = {
        #     "tokens": event["sequences"],
        #     "masks": None,  # event["masks"],     todo update masks!
        #     "values": event["values"],
        # }


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        start_put_in_queue(request["request_ids"], request["execution_id"])

        sequences, past_key_values = llm_model.generate_cache(
            request["tokens"],
            request["masks"],
            request.get("values", None),
            request["config"],
            ResponseStreamer(request["request_ids"], request["execution_id"]) if request["use_stream"] else None
        )
        complete_put_in_queue(
            request["request_ids"],
            request["execution_id"],
            sequences,
            past_key_values,
            request["config"]
        )


def prepare_prompts(prompts):
    global llm_model
    tokens, masks = llm_model.tokenize_prompts(prompts)
    return {
        "tokens": tokens,
        "masks": masks,
        "values": None
    }


def add_prompts_execution(request_ids, prompts, request_config, use_stream=True):
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
        "config": request_config,
        "use_stream": use_stream
    })

    return event_queues[execution_id]
