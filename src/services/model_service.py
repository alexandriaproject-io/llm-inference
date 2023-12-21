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
    ERROR = 6


class LLMInternalEventTypes(enum.Enum):
    START = 1
    PROGRESS = 4
    COMPLETE = 5
    ERROR = 6


llm_model: LLMModel
execution_queue = queue.Queue()
response_queue = queue.Queue()
event_queues = {}
cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)
eos_cache_progress = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)
eos_cache_complete = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)


class ResponseStreamer(BaseStreamer):
    def __init__(self, cache_id, request_ids, execution_id, masks):
        self.cache_id = cache_id
        self.request_ids = request_ids
        self.execution_id = execution_id
        self.masks = masks

    def put(self, value):
        progress_put_in_queue(self.cache_id, self.request_ids, self.execution_id, value, self.masks)

    def end(self):
        return


def request_ids_to_cache_id(request_ids):
    sorted_ids = sorted(request_ids)
    return ''.join(sorted_ids)


def progress_put_in_queue(cache_id, request_ids, execution_id, values, masks):
    global response_queue
    response_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.PROGRESS,
        "tokens": values,
        "masks": masks
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


def error_put_in_queue(cache_id, request_ids, execution_id, error):
    global response_queue
    response_queue.put({
        "cache_id": cache_id,
        "request_ids": request_ids,
        "execution_id": execution_id,
        "type": LLMInternalEventTypes.ERROR,
        "error": error,
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
    global eos_cache_progress
    global eos_cache_complete
    global event_queues
    global llm_model
    while True:
        event = response_queue.get()
        if event is None:  # Use None as a signal to stop the thread
            break
        if not event["execution_id"] in event_queues:
            continue
        cache_id = event["cache_id"]
        execution_id = event["execution_id"]

        # handle start events for batch
        if event["type"] == LLMInternalEventTypes.START:
            start_events = []
            for request_id in event["request_ids"]:
                start_events.append({
                    "request_id": request_id,
                    "type": LLMEventTypes.START
                })
            event_queues[execution_id].put({
                "events_type": LLMEventTypes.START,
                "events": start_events
            })

        # handle progress events for batch
        elif event["type"] == LLMInternalEventTypes.PROGRESS:
            progress_events = []
            eos_state_progress = eos_cache_progress[cache_id] if cache_id in eos_cache_progress else {}
            eos_state_complete = eos_cache_complete[cache_id] if cache_id in eos_cache_complete else {}
            event_type = LLMEventTypes.INITIALIZED if event["tokens"].dim() == 2 else LLMEventTypes.PROGRESS

            for request_id, tokens, mask in zip(event["request_ids"], event["tokens"], event["masks"]):
                # Handle initialization event
                if event_type == LLMEventTypes.INITIALIZED:
                    progress_events.append({
                        "request_id": request_id,
                        "type": LLMEventTypes.INITIALIZED,
                        "text": llm_model.decode_output(tokens[mask == 1])
                    })
                # Handle progress event. Dont forward if reached EOS during complete or stream events
                elif not eos_state_progress.get(request_id, False) and not eos_state_complete.get(request_id, False):
                    cut_tokens, is_eos = llm_model.cut_by_eos(tokens)
                    eos_state_progress[request_id] = is_eos
                    progress_events.append({
                        "request_id": request_id,
                        "type": LLMEventTypes.PROGRESS,
                        "text": llm_model.decode_output(cut_tokens) if not is_eos else llm_model.tokenizer.eos_token,
                    })
                else:
                    # keep array orderly
                    progress_events.append(None)

            # Update streaming eos cache
            eos_cache_progress[cache_id] = eos_state_progress
            event_queues[execution_id].put({
                "events_type": event_type,
                "events": progress_events
            })

        # handle complete events for batch
        elif event["type"] == LLMInternalEventTypes.COMPLETE:
            eos_state_complete = eos_cache_complete[cache_id] if cache_id in eos_cache_complete else {}
            complete_events = []
            masks = []
            total_new_tokens_count = 0
            for request_id, sequence, mask in zip(event["request_ids"], event["sequences"], event["masks"]):
                new_tokens = sequence.size(0) - mask.size(0)
                new_attention_tokens = 0
                if eos_state_complete.get(request_id, False):
                    # Request is done, keep padding it to not break the batch execution
                    new_mask = llm_model.extend_cache_mask(mask, 0, new_tokens)
                else:
                    # Skip initial tokens and check for EOS token, if found cut by first occurrence
                    cut_tokens, is_eos = llm_model.cut_by_eos(sequence, mask.size(0))
                    eos_state_complete[request_id] = is_eos

                    new_attention_tokens = max(0, cut_tokens.size(0) - mask.size(0))
                    new_padding_tokens = new_tokens - new_attention_tokens
                    new_mask = llm_model.extend_cache_mask(mask, new_attention_tokens, new_padding_tokens)

                total_new_tokens_count += new_attention_tokens
                masks.append(new_mask)
                complete_events.append({
                    "type": LLMEventTypes.COMPLETE,
                    "request_id": request_id,
                    "text": llm_model.decode_output(sequence[new_mask == 1]),
                    "new_tokens_count": new_attention_tokens,
                    "is_eos": eos_state_complete[request_id]
                })

            # Update cache statuses
            eos_cache_complete[cache_id] = eos_state_complete
            is_eos_all = all(complete_event["is_eos"] for complete_event in complete_events)
            event_queues[execution_id].put({
                "events_type": LLMEventTypes.COMPLETE,
                "events": complete_events,
                "new_tokens_count": total_new_tokens_count,
                "is_eos_all": is_eos_all
            })

            # Handle caching or clearing of cache for this execution
            if is_eos_all:
                if cache_id in cache:
                    del cache[cache_id]
                if cache_id in eos_cache_progress:
                    del eos_cache_progress[cache_id]
                if cache_id in eos_cache_complete:
                    del eos_cache_complete[cache_id]
            else:
                cache[cache_id] = {
                    "tokens": event["sequences"],
                    "masks": llm_model.stack_masks(masks),
                    "values": event["values"],
                    "config": event["config"]
                }
            # Clean event_queue reference
            if execution_id in event_queues:
                del event_queues[execution_id]

        elif event["type"] == LLMInternalEventTypes.ERROR:
            error_events = []
            for request_id in event["request_ids"]:
                error_events.append({
                    "request_id": request_id,
                    "type": LLMEventTypes.ERROR,
                    "error": event["error"]
                })
            event_queues[execution_id].put({
                "events_type": LLMEventTypes.ERROR,
                "events": error_events,
                "error": event["error"]
            })
            # Clean event_queue reference
            if execution_id in event_queues:
                del event_queues[execution_id]


def handle_model_generation():
    global llm_model

    while True:
        request = execution_queue.get()
        if request is None:  # Use None as a signal to stop the thread
            break

        start_put_in_queue(
            request["cache_id"],
            request["request_ids"],
            request["execution_id"]
        )

        # if no stream is enabled fire initialization event manually
        if not request["use_stream"]:
            progress_put_in_queue(
                request["cache_id"],
                request["request_ids"],
                request["execution_id"],
                request["tokens"],
                request["masks"]
            )

        try:
            sequences, past_key_values = llm_model.generate_cache(
                request["tokens"],
                request["masks"],
                request.get("values", None),
                request["config"],
                ResponseStreamer(
                    request["cache_id"],
                    request["request_ids"],
                    request["execution_id"],
                    request["masks"].clone().to('cpu')
                ) if request["use_stream"] else None
            )
            complete_put_in_queue(
                request["cache_id"],
                request["request_ids"],
                request["execution_id"],
                sequences,
                past_key_values,
                request["masks"],
                request["config"]
            )
        except Exception as error:
            error_put_in_queue(
                request["cache_id"],
                request["request_ids"],
                request["execution_id"],
                error
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
