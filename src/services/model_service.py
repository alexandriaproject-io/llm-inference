from src.models.llm_model_class import LLMModel, BaseStreamer
from src.config import config
import queue
import threading
import enum
import uuid
import time
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
eos_cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)


class ResponseStreamer(BaseStreamer):
    def __init__(self, cache_id, request_ids, execution_id):
        self.cache_id = cache_id
        self.request_ids = request_ids
        self.execution_id = execution_id

    def put(self, value):
        progress_put_in_queue(self.cache_id, self.request_ids, self.execution_id, value)

    def end(self):
        return


def request_ids_to_cache_id(request_ids):
    sorted_ids = sorted(request_ids)
    return ''.join(sorted_ids)


def progress_put_in_queue(cache_id, request_ids, execution_id, values):
    global response_queue
    response_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.PROGRESS,
        "tokens": values
    })


def start_put_in_queue(cache_id, request_ids, execution_id):
    global response_queue
    response_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.START,
    })


def complete_put_in_queue(cache_id, request_ids, execution_id, sequences, past_key_values, masks, request_config):
    global response_queue
    response_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.COMPLETE,
        "config": request_config,
        "sequences": sequences,
        "masks": masks,
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
    global eos_cache
    global event_queues
    global llm_model
    while True:
        event = response_queue.get()
        if event is None:  # Use None as a signal to stop the thread
            break
        if not event["execution_id"] in event_queues:
            continue

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
            eos_item_state = eos_cache[event["cache_id"]] if event["cache_id"] in eos_cache else {}

            for request_id, tokens in zip(event["request_ids"], event["tokens"]):
                if not eos_item_state.get(request_id, False):
                    cut_tokens, is_eos = llm_model.cut_by_eos(tokens)
                    eos_item_state[request_id] = is_eos
                    event_queues[event["execution_id"]].put({
                        "request_id": request_id,
                        "type": event_type,
                        "text": llm_model.decode_output(cut_tokens) if not is_eos else llm_model.tokenizer.eos_token,
                    })

            eos_cache[event["cache_id"]] = eos_item_state

        # handle complete events for batch
        elif event["type"] == LLMInternalEventTypes.COMPLETE:
            eos_item_state = eos_cache[event["cache_id"]] if event["cache_id"] in eos_cache else {}
            is_execution_eos = True
            data = []
            masks = []
            for request_id, sequence, mask in zip(event["request_ids"], event["sequences"], event["masks"]):
                cut_tokens, is_eos = llm_model.cut_by_eos(sequence)
                eos_item_state[request_id] = is_eos
                is_execution_eos = is_execution_eos and is_eos

                new_attention_tokens = cut_tokens.size(0) - mask.size(0)
                new_padding_tokens = sequence.size(0) - mask.size(0) - new_attention_tokens
                masks.append(llm_model.extend_cache_mask(mask, new_attention_tokens, new_padding_tokens))

                data.append({
                    "request_id": request_id,
                    "text": llm_model.decode_output(cut_tokens),
                    "is_eos": is_eos
                })

            event_queues[event["execution_id"]].put({
                "type": LLMEventTypes.COMPLETE,
                "data": data,
                "is_eos": is_execution_eos
            })

            # Handle caching or clearing of cache for this execution
            if is_execution_eos:
                if event["cache_id"] in cache:
                    del cache[event["cache_id"]]
                if event["cache_id"] in eos_cache:
                    del eos_cache[event["cache_id"]]
            else:
                cache[event["cache_id"]] = {
                    "tokens": event["sequences"],
                    "masks": llm_model.stack_masks(masks),
                    "values": event["values"],
                    "config": event["config"]
                }


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        start_put_in_queue(request["cache_id"], request["request_ids"], request["execution_id"])
        start_time = time.perf_counter()
        sequences, past_key_values = llm_model.generate_cache(
            request["tokens"],
            request["masks"],
            request.get("values", None),
            request["config"],
            ResponseStreamer(
                request["cache_id"],
                request["request_ids"],
                request["execution_id"]
            ) if request["use_stream"] else None
        )
        print(f"Execution time {time.perf_counter() - start_time} seconds")
        complete_put_in_queue(
            request["cache_id"],
            request["request_ids"],
            request["execution_id"],
            sequences,
            past_key_values,
            request["masks"],
            request["config"]
        )


def prepare_prompts(prompts, request_config):
    global llm_model
    tokens, masks = llm_model.tokenize_prompts(prompts)
    return {
        "tokens": tokens,
        "masks": masks,
        "values": None,
        "config": request_config or {}
    }


def add_prompts_execution(request_ids, prompts, request_config, use_stream=True):
    global cache
    cache_id = request_ids_to_cache_id(request_ids)
    execution_id = uuid.uuid4()
    target = cache[cache_id] if cache_id in cache else prepare_prompts(prompts, request_config)

    event_queues[execution_id] = queue.Queue()
    execution_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "tokens": target["tokens"],
        "masks": target["masks"],
        "values": target["values"],
        "config": request_config if request_config is not None else target["config"],
        "use_stream": use_stream
    })

    return event_queues[execution_id]
