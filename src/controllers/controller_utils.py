def is_valid_config(generation_config):
    if generation_config:
        if not isinstance(generation_config, dict):
            return False
        for key, value in generation_config.items():
            if key in ['num_beams', 'max_new_tokens', 'top_k'] and not isinstance(value, int):
                return False
            elif key in ['do_sample', 'stream'] and not isinstance(value, bool):
                return False
            elif key in ['temperature', 'top_p', 'repetition_penalty', 'length_penalty'] \
                    and not (isinstance(value, float) or isinstance(value, int)):
                return False
    return True


def is_valid_batch_item(batch_item):
    request_id = batch_item.get("request_id", '')
    prompt = batch_item.get("prompt", " ")
    return request_id and isinstance(request_id, str) and isinstance(prompt, str)


def is_valid_batch(batch):
    return len(batch) > 0 and all(is_valid_batch_item(prompt) for prompt in batch)
