from flask import Flask, request, jsonify
from llm_model_handler import LLMModel
import config
import time
import torch


llm_model = LLMModel(config.MODEL_PATH, config.BASE_MODEL_CONFIG)
llm_model.load_model()
llm_model.run_model()




start_prompt = "Generate a very very long poem about 1000 cats"
def full_gen_test():
    tokens, attention_mask, input_ids = llm_model.tokenize_prompt(start_prompt)

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

def token_by_token_test(clear_cache = False):
    past_key_values = None
    generated_sequence = []
    tokens, attention_mask, input_ids = llm_model.tokenize_prompt(start_prompt)

    start_time = time.perf_counter()
    while True:
        # Generate output using the provided function
        outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, past_key_values,
                                                            {"temperature": 0, "max_new_tokens": 1, "clear_cache": clear_cache})

        # Extract the last token from the sequence
        next_token_id = outputs[:, -1].item()
        generated_sequence.append(next_token_id)

        # Check for end of sequence
        if next_token_id == llm_model.tokenizer.eos_token_id:
            break

        # Update tokens for the next iteration (append the new token)
        tokens = torch.cat((tokens, outputs[:, -1].unsqueeze(0)), dim=1)
        attention_mask = torch.cat((attention_mask, torch.ones((attention_mask.shape[0], 1)).to(attention_mask.device)),
                                   dim=1)

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"1 token at a time (clear cache:{clear_cache}) {execution_time} seconds - {len(generated_sequence)} tokens - {len(generated_sequence)/execution_time} t/s")


def token_by_token_test_10(clear_cache = False):
    past_key_values = None
    generated_sequence = []
    tokens, attention_mask, input_ids = llm_model.tokenize_prompt(start_prompt)

    start_time = time.perf_counter()
    while True:
        # Generate output using the provided function
        outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, past_key_values,
                                                            {"temperature": 0, "max_new_tokens": 10,  "clear_cache": clear_cache})

        new_tokens = outputs[0, -10:]  # Change here to get the last 10 tokens
        generated_sequence.extend(new_tokens.tolist())

        # Check for end of sequence in the new tokens
        if llm_model.tokenizer.eos_token_id in new_tokens:
            break

        # Update tokens for the next iteration (append the new tokens)
        tokens = torch.cat((tokens, new_tokens.unsqueeze(0)), dim=1)
        # Update attention mask for the new tokens
        attention_mask = torch.cat((attention_mask, torch.ones((1, new_tokens.shape[0])).to(attention_mask.device)), dim=1)


    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"10 tokens at a time (clear cache:{clear_cache}): {execution_time} seconds - {len(generated_sequence)} tokens - {len(generated_sequence)/execution_time} t/s")


def token_by_token_test_1000():
    past_key_values = None
    generated_sequence = []
    tokens, attention_mask, input_ids = llm_model.tokenize_prompt(start_prompt)

    start_time = time.perf_counter()
    while True:
        # Generate output using the provided function
        outputs, past_key_values = llm_model.generate_cache(tokens, attention_mask, past_key_values,
                                                            {"temperature": 0, "max_new_tokens": 1000})

        # Extract the last token from the sequence
        next_token_id = outputs[:, -1].item()
        generated_sequence.append(next_token_id)

        # Check for end of sequence
        if next_token_id == llm_model.tokenizer.eos_token_id:
            break

        # Update tokens for the next iteration (append the new token)
        tokens = torch.cat((tokens, outputs[:, -1].unsqueeze(0)), dim=1)
        attention_mask = torch.cat((attention_mask, torch.ones((attention_mask.shape[0], 1)).to(attention_mask.device)),
                                   dim=1)

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"1000 tokens at a time {execution_time} seconds - {731} tokens - {731/execution_time} t/s")


print("Running 10 token test generation")

start_time = time.perf_counter()
llm_model.generate_full(start_prompt, {"temperature": 0, "max_new_tokens": 10})
end_time = time.perf_counter()
execution_time = end_time - start_time
print(f"Test full pass: {execution_time} seconds - {10/execution_time} tokens/sec")

print("")

token_by_token_test()       # 23.3 seconds
token_by_token_test()       # 23.3 seconds
token_by_token_test()       # 23.3 seconds
token_by_token_test()       # 23.3 seconds
token_by_token_test()       # 23.3 seconds
token_by_token_test(True)       # 23.3 seconds
token_by_token_test(True)       # 23.3 seconds
token_by_token_test(True)       # 23.3 seconds
token_by_token_test(True)       # 23.3 seconds
token_by_token_test(True)       # 23.3 seconds
token_by_token_test_10()    # 21.09 seconds
token_by_token_test_10()    # 21.09 seconds
token_by_token_test_10()    # 21.09 seconds
token_by_token_test_10()    # 21.09 seconds
token_by_token_test_10()    # 21.09 seconds
token_by_token_test_10(True)    # 21.09 seconds
token_by_token_test_10(True)    # 21.09 seconds
token_by_token_test_10(True)    # 21.09 seconds
token_by_token_test_10(True)    # 21.09 seconds
token_by_token_test_10(True)    # 21.09 seconds
token_by_token_test_1000()  # 20.85 seconds
token_by_token_test_1000()  # 20.85 seconds
token_by_token_test_1000()  # 20.85 seconds
token_by_token_test_1000()  # 20.85 seconds
token_by_token_test_1000()  # 20.85 seconds
full_gen_test()             # 20.73 seconds
full_gen_test2()            # 20.86 seconds

print("")






app = Flask(__name__)

if __name__ == "__main__":
    # DO NOT USE reloader, this ends up loading the model twice!
    app.run(debug=True, host=config.SERVER_HOST, port=config.SERVER_PORT, use_reloader=False)
