from logger import log
import llama_cpp
from src.models.llama_cpp.utils import MockTensor
from src.config import config


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
        self.model = llama_cpp.Llama(
            model_path=self.model_path,
            n_ctx=config.LLAMA_CPP_MAX_CONTEXT,
            n_batch=config.LLAMA_CPP_BATCH_TOKENS,
        )
        self.model.set_seed(self.config['MODEL_SEED'])
        self.tokenizer = self.model.tokenizer()
        self.cache = llama_cpp.LlamaRAMCache(1024 * 1024 * config.LLAMA_RAM_CACHE_MB)  # 512mb of cache
        self.model.set_cache(self.cache)

    def run_model(self):
        self.isReady = True
        log.info(f"Model is ready to go.")

    def generate_cache(self, prompts, attention_mask, past_key_values, config, streamer=None):
        if not self.isReady:
            raise NotReadyException("Model not ready.Please Use Model.load_model(path, config) and Model.run_model()")
        log.warn("'num_beams' and 'do_sample' are not supported. num_beams is always 1 and do_sample always true")
        responses = [[prompt] for prompt in prompts]
        if (len(prompts) > 1):
            log.warn("llama_ccp doesnt support batching. The prompts will be handled one by one, this will be slow")
            if streamer:
                log.warn("Not Yet")
            else:
                for index, prompt in enumerate(prompts):
                    if not prompt.endswith('</s>'):
                        output = self.model.create_completion(
                            prompt,
                            max_tokens=int(config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"])),
                            temperature=float(config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"])),
                            top_p=float(config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"])),
                            top_k=int(config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"])),
                            repeat_penalty=float(
                                config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"])),
                            presence_penalty=float(
                                config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"])),
                        )

                        responses[index].append(output["choices"][0]["text"])
                        # Nasty work around to mimic the GPU model behaviour without going too technical
                        new_tokens = output["usage"]["completion_tokens"]
                        if output["choices"][0]['finish_reason'] == "stop":
                            responses[index].append('</s>')
                            pad_tokens = new_tokens - 1
                        else:
                            pad_tokens = new_tokens

                        if pad_tokens > 0:
                            for i in range(pad_tokens):
                                responses[index].append('')

        else:
            if streamer:
                streamer.put(MockTensor(prompts, 2))
                stream = self.model.create_completion(
                    prompts[0],
                    max_tokens=int(config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"])),
                    temperature=float(config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"])),
                    top_p=float(config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"])),
                    top_k=int(config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"])),
                    repeat_penalty=float(config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"])),
                    presence_penalty=float(
                        config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"])),
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
            else:
                output = self.model.create_completion(
                    prompts[0],
                    max_tokens=int(config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"])),
                    temperature=float(config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"])),
                    top_p=float(config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"])),
                    top_k=int(config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"])),
                    repeat_penalty=float(config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"])),
                    presence_penalty=float(
                        config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"])),
                )

                responses[0].append(output["choices"][0]["text"])
                # Nasty work around to mimic the GPU model behaviour without going too technical
                new_tokens = output["usage"]["completion_tokens"]
                if output["choices"][0]['finish_reason'] == "stop":
                    text = '</s>'
                    responses[0].append(text)
                    pad_tokens = new_tokens - 1
                else:
                    pad_tokens = new_tokens

                if pad_tokens > 0:
                    for i in range(pad_tokens):
                        responses[0].append('')
        return responses, None
