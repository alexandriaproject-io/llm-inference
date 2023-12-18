from flask import Flask, request, jsonify
from src.config import config
import time
import torch
import queue
from src.models.llm_model_class import LLMModel

llm_model = LLMModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
llm_model.load_model()
llm_model.run_model()

start_prompt = "[INST] Generate a very long poem about 1000 cats [/INST]\n\n"
execution_queue = queue.Queue()


def full_gen_test():
    tokens, attention_mask, input_ids = llm_model.tokenize_prompts(start_prompt)

    start_time = time.perf_counter()
    outputs = llm_model.generate_cache(tokens, attention_mask, None, {"temperature": 0, "max_new_tokens": 1000})
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"New full pass {execution_time} seconds")


def full_gen_test2():
    start_time = time.perf_counter()
    llm_model.generate_full(start_prompt, {"temperature": 0, "max_new_tokens": 1000})
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Old full pass: {execution_time} seconds")


def token_by_token_test():
    past_key_values = None
    generated_sequence = []
    tokens, attention_mask = llm_model.tokenize_prompt(start_prompt)

    start_time = time.perf_counter()

    m_execution_time = 0
    execution_queue.put({
        "tokens": tokens,
        "attention_mask": attention_mask,
        "past_key_values": None
    })
    while True:
        req = execution_queue.get()

        # Generate output using the provided function
        outputs, past_key_values = llm_model.generate_cache(
            req["tokens"],
            req["attention_mask"],
            req["past_key_values"],
            {"temperature": 0, "max_new_tokens": 1})

        m_start_time = time.perf_counter()
        # Extract the last token from the sequence
        next_token_id = outputs[:, -1].item()
        generated_sequence.append(next_token_id)

        # Check for end of sequence
        if next_token_id == llm_model.tokenizer.eos_token_id:
            break


        # Update tokens for the next iteration (append the new token)
        attention_mask = torch.cat((attention_mask, torch.ones((attention_mask.shape[0], 1)).to(attention_mask.device)),
                                   dim=1)
        m_execution_time += time.perf_counter() - m_start_time

        execution_queue.put({
            "tokens": outputs,
            "attention_mask": attention_mask,
            "past_key_values": past_key_values
        })

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(
        f"1 token at a time {m_execution_time} / {execution_time} seconds - {len(generated_sequence)} tokens - {len(generated_sequence) / execution_time} t/s")
    return len(generated_sequence) / execution_time


def token_by_token_test_10():
    past_key_values = None
    generated_sequence = []
    tokens, attention_mask = llm_model.tokenize_prompt(start_prompt)
    tokens_len = len(tokens[0])
    start_time = time.perf_counter()
    while True:
        # Generate output using the provided function
        outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, past_key_values,
                                                            {"temperature": 0, "max_new_tokens": 10})

        new_tokens = outputs[0, -10:]  # Change here to get the last 10 tokens
        generated_sequence.extend(new_tokens.tolist())

        # Check for end of sequence in the new tokens
        if llm_model.tokenizer.eos_token_id in new_tokens:
            break

        # Update tokens for the next iteration (append the new tokens)
        tokens = outputs  # torch.cat((tokens, new_tokens.unsqueeze(0)), dim=1)
        # Update attention mask for the new tokens
        attention_mask = torch.cat((attention_mask, torch.ones((1, new_tokens.shape[0])).to(attention_mask.device)),
                                   dim=1)

    new_tokens_len = len(outputs[0]) - tokens_len
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(
        f"10 tokens at a time {execution_time} seconds - {new_tokens_len} tokens - {new_tokens_len / execution_time} t/s")
    return new_tokens_len / execution_time


def token_by_token_test_1000():
    tokens, attention_mask = llm_model.tokenize_prompt(start_prompt)
    start_time = time.perf_counter()
    outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, None,
                                                        {"temperature": 0, "max_new_tokens": 1000})
    new_tokens_len = len(outputs[0]) - len(tokens[0])
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(
        f"1000 tokens at a time {execution_time} seconds - {new_tokens_len} tokens - {new_tokens_len / execution_time} t/s")
    return new_tokens_len / execution_time


def batch_tokens(use_second_prompt, max_count):
    target = [start_prompt]
    if use_second_prompt:
        target.append("Generate a very very long poem about 1000 dogs")
        target.append("Generate a very very long poem about 10000 horses")
        target.append("Generate a very very long poem about 1000 goats")
        target.append("Generate a very very long poem about 10000 birds")
        target.append("Generate a very very long poem about 1000 shoes and boots")
        target.append("Generate a very very long poem about 1000 boats")
    tokens, attention_mask = llm_model.tokenize_prompts(
        target
    )

    start_time = time.perf_counter()

    outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, None,
                                                        {"temperature": 0, "max_new_tokens": max_count})
    end_time = time.perf_counter()

    last_new_line = False

    pad_token_id = llm_model.tokenizer.pad_token_id
    output_length = 0
    for output in outputs:
        out_len = 0
        new_line_count = 0
        for out_token in output:
            if out_token.item() != pad_token_id:
                out_len += 1
                if out_token.item() == 13:
                    new_line_count += 1
                    if new_line_count == 10:
                        out_len -= 10
                        break
                else:
                    new_line_count = 0
        output_length += out_len

    for input_token in tokens:
        for in_token in input_token:
            if in_token != pad_token_id:
                output_length -= 1

    new_tokens_len = output_length
    execution_time = end_time - start_time
    print(
        f"{max_count} tokens at a time ( batch mode {'multiple' if use_second_prompt else 'single'} ) {execution_time} seconds - {new_tokens_len} tokens - {new_tokens_len / execution_time} t/s")
    return new_tokens_len / execution_time


print("Running 10 token test generation")

warmup_start_time = time.perf_counter()
res, is_eos = llm_model.generate_full("Write a warm up poem", {"temperature": 0, "max_new_tokens": 10})
print("####")
print(res)
print("####")
warmup_end_time = time.perf_counter()
warmup_execution_time = warmup_end_time - warmup_start_time
print(f"Warmup pass: {warmup_execution_time} seconds - {10 / warmup_execution_time} tokens/sec")

print("")
print("")

batch_tokens(True, 10)
batch_tokens(False, 10)

batch_tokens(True, 100)
batch_tokens(False, 100)
#
# batch_tokens(True, 500)
# batch_tokens(False, 500)

avg = token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
avg += token_by_token_test()
print(f"1 Token at a time - Average {avg / 10} t/s")

avg = token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()
avg += token_by_token_test_10()

print(f"10 Tokens at a time - Average {avg / 10} t/s")

avg = token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
avg += token_by_token_test_1000()
print(f"1000 Token once - Average {avg / 10} t/s")

print("")

app = Flask(__name__)

if __name__ == "__main__":
    # DO NOT USE reloader, this ends up loading the model twice!
    app.run(debug=True, host=config.SERVER_HOST, port=config.SERVER_PORT, use_reloader=False)
