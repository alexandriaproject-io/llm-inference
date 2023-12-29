from logger import log
import llama_cpp
from src.models.llama_cpp.utils import MockTensor


class NotReadyException(Exception):
    def __init__(self, message="Component is not ready"):
        self.message = message
        super().__init__(self.message)


class LLMCPPModel:
    def __init__(self, model_path, config):
        self.isReady = False
        self.tokenizer = None
        self.model = None
        self.config = config
        self.model_path = model_path
        self.device = "cpu"
        self.cache = None

    def load_model(self):
        self.model = llama_cpp.Llama(model_path=self.model_path)
        self.model.set_seed(self.config['MODEL_SEED'])
        self.tokenizer = self.model.tokenizer()
        self.cache = llama_cpp.LlamaRAMCache(1024 * 1024 * 512)  # 512mb of cache
        self.model.set_cache(self.cache)

    def run_model(self):
        self.isReady = True
        log.info(f"Model is ready to go.")

    def generate_cache(self, prompts, attention_mask, past_key_values, config, streamer=None):
        if not self.isReady:
            raise NotReadyException("Model not ready.Please Use Model.load_model(path, config) and Model.run_model()")

        streamer.put(MockTensor(prompts, 2))

        responses = [[prompt] for prompt in prompts]

        if streamer:
            if (len(prompts) > 1):
                log.warn("llama_ccp doesnt support batching, this will be slow")

            else:
                stream = self.model(
                    prompts[0],
                    max_tokens=int(config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"])),
                    stream=True
                )
                for output in stream:
                    text = output["choices"][0]["text"]
                    responses[0].append(text)
                    streamer.put(MockTensor([text], 1))
                    if output["choices"][0]['finish_reason'] == "stop":
                        text = '</s>'
                        responses[0].append(text)
                        streamer.put(MockTensor([text], 1))

        return responses, None
