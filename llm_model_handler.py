from transformers import AutoModelForCausalLM, AutoTokenizer
from logger import log
import torch


class LLMModel:
    def __init__(self, model_path, config):
        self.isReady = False
        self.tokenizer = None
        self.model = None
        self.config = config
        self.model_path = model_path
        self.device = "cuda" if self.config["ENABLE_CUDA"] and torch.cuda.is_available() else "cpu"
        self.isBF16Supported = False if not self.config["ENABLE_CUDA"] else torch.cuda.is_bf16_supported()
        self.is8bitQuantized = self.config["LOAD_IN_8BIT"]

        if self.is8bitQuantized:
            self.model_type = None # 4bit and 8bit quantization defaults to its own parameters
        elif self.device == "cuda":
            self.model_type = torch.bfloat16 if self.isBF16Supported else torch.float16
        else:
            self.model_type = torch.float32

    def load_model(self):
        log.info(f"Target model: {self.model_path} using seed {self.config['MODEL_SEED']}")
        torch.cuda.manual_seed(self.config["MODEL_SEED"])
        torch.manual_seed(self.config["MODEL_SEED"])
        log.info("Loading model from disk. Be patient this can take a while...")

        low_mem_mode = self.is8bitQuantized or self.config["LOW_CPU_MEM_USAGE"]
        device_map = None
        if low_mem_mode:
            device_map = 'cpu' if self.device == 'cpu' else self.config["TARGET_GPU_INDEX"]

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            return_dict=True,
            load_in_8bit=self.is8bitQuantized,
            device_map=device_map,
            torch_dtype=self.model_type,
            low_cpu_mem_usage=low_mem_mode
        )
        log.info("Model loaded.")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, padding_size="left")
        self.tokenizer.add_special_tokens({"pad_token": "<PAD>"})
        log.info("Tokenizer loaded.")

    def run_model(self):
        if not self.config["LOW_CPU_MEM_USAGE"] and not self.isQuantized:
            log.info(f"Transferring model to gpu")
            self.model.to(self.device)
        log.info(f"Evaluating the model.")
        self.model.eval()
        self.isReady = True
        log.info(f"Model is ready to go.")

    def decode_outputs(self, outputs):
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def tokenize_prompt(self, prompt):
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_tensor = torch.tensor(input_ids)

        attention_mask = (input_tensor != self.tokenizer.pad_token_id).int().unsqueeze(0).to(self.device)
        tokens = torch.tensor(input_ids).long()
        tokens = tokens.unsqueeze(0).to(self.device)
        return tokens, attention_mask, input_ids

    def generate(self, tokens, attention_mask, config):
        with torch.no_grad():
            outputs = self.model.generate(
                tokens,
                attention_mask=attention_mask,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=self.config["ENABLE_USE_CACHE"],
                num_beams=config.get("num_beams", self.config["MODEL_DEFAULT_NUM_BEAMS"]),
                do_sample=config.get("do_sample", self.config["MODEL_DEFAULT_DO_SAMPLE"]),
                temperature=config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"]),
                top_p=config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"]),
                top_k=config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"]),
                max_new_tokens=config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"]),
                repetition_penalty=config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"]),
                length_penalty=config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"]),
            )
        return outputs

    def generate_cache(self, input_ids, attention_mask, past_key_values, config):
        with torch.no_grad():
            # Generate sequences with updated past_key_values
            model_output = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                past_key_values=past_key_values,
                use_cache=True,  # Ensure caching is enabled
                return_dict_in_generate=True,  # Return a dictionary containing past_key_values
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                num_beams=config.get("num_beams", self.config["MODEL_DEFAULT_NUM_BEAMS"]),
                do_sample=config.get("do_sample", self.config["MODEL_DEFAULT_DO_SAMPLE"]),
                temperature=config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"]),
                top_p=config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"]),
                top_k=config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"]),
                max_new_tokens=config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"]),
                repetition_penalty=config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"]),
                length_penalty=config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"]),
            )

        # Extract sequences and updated past_key_values
        sequences = model_output.sequences
        new_past_key_values = model_output.past_key_values if 'past_key_values' in model_output else None

        return sequences, new_past_key_values

    def generate_full(self, prompt, config):
        (tokens, attention_mask, input_ids) = self.tokenize_prompt(prompt)

        outputs = self.generate(tokens, attention_mask, config)
        output_text = self.decode_outputs(outputs)
        response_start_index = len(prompt)
        response = output_text[response_start_index:].strip()
        # TODO - use tokens to cut and decode outputs instead of text cutting...

        is_eos = outputs[0][-1] == self.tokenizer.eos_token_id

        return response,  is_eos

    def generate_stream(self, prompt, stream_callback, finish_callback):
        (tokens, attention_mask) = self.tokenizer(prompt)
