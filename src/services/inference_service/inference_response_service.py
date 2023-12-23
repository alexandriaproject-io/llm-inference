from cachetools import TTLCache
from src.config import config
from src.config.types import LLMEventTypes
from src.models.llm_tokenizer import LLMTokenizer
from src.services.inference_service.utils import LLMInternalEventTypes


def handle_model_responses(response_queue, events_queue, tokenizer_config, cache, execution_cache):
    eos_cache_progress = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)
    eos_cache_complete = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)
    tokenizer = LLMTokenizer(config.MODEL_PATH, tokenizer_config)

    while True:
        event = response_queue.get()
        if event is None:  # Use None as a signal to stop the thread
            break

        execution_id = event["execution_id"]
        execution = execution_cache[execution_id]
        cache_id = execution["cache_id"]

        # handle start events
        if event["type"] == LLMInternalEventTypes.START:
            events_queue.put({
                "events_type": LLMEventTypes.START,
                "execution_id": execution_id,
                "events": [{
                    "request_id": request_id,
                    "type": LLMEventTypes.START
                } for request_id in execution["request_ids"]]
            })

        # handle initialization events
        elif event["type"] == LLMInternalEventTypes.INITIALIZED:
            events_queue.put({
                "events_type": LLMEventTypes.INITIALIZED,
                "execution_id": execution_id,
                "events": [{
                    "request_id": request_id,
                    "type": LLMEventTypes.INITIALIZED,
                    "tokens": token[mask == 1].to('cpu')
                } for token, mask, request_id in zip(event["tokens"], execution["masks"], execution["request_ids"])]
            })

        # handle progress events
        elif event["type"] == LLMInternalEventTypes.PROGRESS:
            eos_state_progress = eos_cache_progress.get(cache_id, {})
            eos_state_complete = eos_cache_complete.get(cache_id, {})

            progress_events = []
            for token, mask, request_id in zip(event["tokens"], execution["masks"], execution["request_ids"]):
                is_request_eos = eos_state_progress.get(request_id, False) or eos_state_complete.get(request_id, False)
                if not is_request_eos:
                    eos_state_progress[request_id] = tokenizer.is_eos_token(token)
                    progress_events.append({
                        "request_id": request_id,
                        "type": LLMEventTypes.PROGRESS,
                        "token": token.to('cpu'),
                    })
                else:
                    progress_events.append(None)  # keep array orderly

            eos_cache_progress[cache_id] = eos_state_progress
            events_queue.put({
                "events_type": LLMEventTypes.PROGRESS,
                "execution_id": execution_id,
                "events": progress_events
            })

        # handle complete events
        elif event["type"] == LLMInternalEventTypes.COMPLETE:
            eos_state_complete = eos_cache_complete.get(cache_id, {})

            complete_events = []
            masks = []
            total_new_tokens_count = 0
            for sequence, mask, request_id in zip(event["sequences"], execution["masks"], execution["request_ids"]):
                att_tokens = 0
                pad_tokens = sequence.size(0) - mask.size(0)
                if not eos_state_complete.get(request_id, False):
                    cut_tokens, eos_state_complete[request_id] = tokenizer.cut_by_eos(sequence, mask.size(0))
                    att_tokens = max(0, cut_tokens.size(0) - mask.size(0))
                    pad_tokens = pad_tokens - att_tokens
                masks.append(new_mask := tokenizer.extend_cache_mask(mask, att_tokens, pad_tokens))
                complete_events.append({
                    "type": LLMEventTypes.COMPLETE,
                    "request_id": request_id,
                    "tokens": sequence[new_mask == 1].to('cpu'),
                    "is_eos": eos_state_complete[request_id]
                })

            events_queue.put({
                "events_type": LLMEventTypes.COMPLETE,
                "execution_id": execution_id,
                "events": complete_events,
                "is_eos_all": (is_eos_all := all(e["is_eos"] for e in complete_events))
            })

            # Handle caching or clearing of cache for this execution
            if is_eos_all:
                for cache_dict in (cache, eos_cache_progress, eos_cache_complete):
                    cache_dict.pop(cache_id, None)
            else:
                eos_cache_complete[cache_id] = eos_state_complete
                cache[cache_id] = {
                    "tokens": event["sequences"],
                    "masks": tokenizer.stack_masks(masks),
                    "values": event["values"],
                    "config": execution["config"]
                }

        # Handle execution error event
        elif event["type"] == LLMInternalEventTypes.ERROR:
            events_queue.put({
                "events_type": LLMEventTypes.ERROR,
                "execution_id": execution_id,
                "error": event["error"],
                "events": [
                    {"request_id": request_id, "type": LLMEventTypes.ERROR, "error": event["error"]}
                    for request_id in event["request_ids"]
                ]
            })
