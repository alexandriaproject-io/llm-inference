record = ApiBatchPromptRequest()
record.prompts = []
record.prompts.append(
    SinglePrompt(request_id="YmFzZTY0", prompt="[INST] Generate a very long poem about 1000 cats [/INST]\n\n"))
record.prompts.append(
    SinglePrompt(request_id="rFERfgE", prompt="[INST] Generate a short poem about 1000 dogs [/INST]\n\n"))
record.generation_config = GenerationConfig(
    num_beams=1,
    temperature=1,
    max_new_tokens=100
)

transport = TTransport.TMemoryBuffer()
protocol = TBinaryProtocol.TBinaryProtocol(transport)
record.write(protocol)

file_path = "record2.pkl"
with open(file_path, "wb") as binary_file:
    # Write bytes to file
    binary_file.write(transport.getvalue())