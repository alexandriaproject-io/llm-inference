# https://github.com/abetlen/llama-cpp-python/tree/main/examples

from llama_cpp import Llama
import json

llm = Llama(model_path="models/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_0.gguf")

stream = llm(
    "[INST] Generate a very long poem about 1000 cats [/INST]\n\n",
    max_tokens=10000,
    stream=True,

)

tokens = 0
response = ""
for output in stream:
    tokens += 1
    response += output["choices"][0]["text"]
    print(output["choices"][0]["text"])

print(tokens)
print(response)

# https://github.com/abetlen/llama-cpp-python/blob/main/examples/low_level_api/low_level_api_chat_cpp.py