import queue
import threading
import time
from cachetools import TTLCache
from src.config import config
from src.models.huggingface.llm_model_class import LLMModel
from src.models.llama_cpp.llm_cpp_model_class import LLMCPPModel
from src.services.inference_service.utils import check_request_cache, ResponseQueueStreamer, LLMInternalEventTypes
from src.services.inference_service.inference_response_service import handle_model_responses, handle_cpp_model_responses

import src.models.huggingface as huggingface


def start_model_generator(execution_queue, events_queue, ready_event):
    response_queue = queue.Queue()
    cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)
    execution_cache = TTLCache(maxsize=config.MAX_CACHE_SIZE, ttl=config.MAX_CACHE_TTL)

    if config.USE_LLAMA_CPP:
        llm_model = LLMCPPModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
        llm_model.load_model()
        llm_model.run_model()
        threading.Thread(
            target=handle_cpp_model_responses,
            args=(response_queue, events_queue, execution_cache, cache),
            daemon=True
        ).start()
    else:
        llm_model = LLMModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
        llm_model.load_model()
        llm_model.run_model()

        tokenizer_config = {"device": llm_model.device, "SPACE_TOKEN_CHAR": config.SPACE_TOKEN_CHAR}
        threading.Thread(
            target=handle_model_responses,
            args=(response_queue, events_queue, tokenizer_config, cache, execution_cache),
            daemon=True
        ).start()

    ready_event.set()

    try:
        while True:
            request = execution_queue.get()

            if request is None:  # Use None as a signal to stop the thread
                print("Stopping generation process...")
                break
            if request["execution_id"] in execution_cache:
                print("Ignoring duplicate execution run.")
                continue

            execution_id = request["execution_id"]
            request_ids = request["request_ids"]
            cache_id = '-'.join(request_ids)
            tokens, masks, values, req_config = check_request_cache(cache, cache_id, request, llm_model.device)

            # to avoid sending these in every event we put them as execution cache
            execution_cache[execution_id] = {
                "cache_id": cache_id,
                "request_ids": request_ids,
                "tokens": tokens,
                "masks": masks.to('cpu'),
                "config": req_config
            }

            response_queue.put({
                "type": LLMInternalEventTypes.START,
                "execution_id": request["execution_id"],
            })

            # if no stream is enabled fire initialization event manually
            if not request["use_stream"]:
                response_queue.put({
                    "type": LLMInternalEventTypes.INITIALIZED,
                    "execution_id": request["execution_id"],
                    "tokens": tokens,
                })

            try:
                start = time.perf_counter()
                sequences, past_key_values = llm_model.generate_cache(
                    tokens,
                    masks,
                    values,
                    req_config,
                    ResponseQueueStreamer(response_queue, execution_id) if request["use_stream"] else None
                )
                response_queue.put({
                    "type": LLMInternalEventTypes.COMPLETE,
                    "execution_id": execution_id,
                    "sequences": sequences,
                    "values": past_key_values,
                    "execution_time": time.perf_counter() - start
                })
            except Exception as error:
                response_queue.put({
                    "type": LLMInternalEventTypes.ERROR,
                    "execution_id": request["execution_id"],
                    "error": error,
                })
    except KeyboardInterrupt:
        events_queue.put(None)
        print("Shutting down model generator.")
