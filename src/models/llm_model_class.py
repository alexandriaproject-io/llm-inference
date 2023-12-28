from transformers import AutoModelForCausalLM, AutoTokenizer
from logger import log
import torch


class BaseStreamer:
    """
    Base class from which `.generate()` streamers should inherit.
    """

    def put(self, value):
        """Function that is called by `.generate()` to push new tokens"""

    def end(self):
        # print("end")
        """Function that is called by `.generate()` to signal the end of generation"""


class NotReadyException(Exception):
    def __init__(self, message="Component is not ready"):
        self.message = message
        super().__init__(self.message)


class LLMModel:
    def __init__(self, model_path, config):
        self.isReady = False
        self.tokenizer = None
        self.model = None
        self.config = config
        self.model_path = model_path
        self.device = "cuda" if self.config["ENABLE_CUDA"] and torch.cuda.is_available() else "cpu"
        self.isBF16Supported = False if not self.config["ENABLE_CUDA"] else torch.cuda.is_bf16_supported()
        self.is8bitQuantized = self.config["LOAD_IN_8BIT"] and not self.config["LOAD_IN_4BIT"]
        self.is4bitQuantized = self.config["LOAD_IN_4BIT"]
        self.isQuantized = self.is8bitQuantized or self.is4bitQuantized

        if self.isQuantized or self.device == "cpu":
            self.model_type = None
        else:
            self.model_type = torch.bfloat16 if self.isBF16Supported else torch.float16

    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, padding_side="left")
        self.tokenizer.pad_token = self.tokenizer.pad_token or self.tokenizer.bos_token
        self.tokenizer.add_special_tokens({"pad_token": self.tokenizer.pad_token})

    def load_model(self):
        log.info(f"Target model: {self.model_path} using seed {self.config['MODEL_SEED']}")
        torch.cuda.manual_seed(self.config["MODEL_SEED"])
        torch.manual_seed(self.config["MODEL_SEED"])
        log.info("Loading model from disk. Be patient this can take a while...")
        low_mem_mode = self.isQuantized or self.config["LOW_CPU_MEM_USAGE"]

        if low_mem_mode:
            device_map = 'cpu' if self.device == 'cpu' else self.config["TARGET_GPU_INDEX"]
        else:
            device_map = None

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            return_dict=True,
            load_in_8bit=self.is8bitQuantized,
            load_in_4bit=self.is4bitQuantized,
            device_map=device_map,
            torch_dtype=self.model_type,
            low_cpu_mem_usage=low_mem_mode
        )
        log.info("Model loaded.")
        self.load_tokenizer()
        self.model.generation_config.pad_token_id = self.model.config.pad_token_id or self.model.config.bos_token_id
        log.info("Tokenizer loaded.")

    def run_model(self):
        if not self.config["LOW_CPU_MEM_USAGE"] and not self.isQuantized:
            log.info(f"Transferring model to gpu")
            self.model.to(self.device)
        log.info(f"Evaluating the model.")
        self.model.eval()
        self.isReady = True
        log.info(f"Model is ready to go.")

    def cut_by_eos(self, output, skip_tokens=0):
        if output.numel() == 1:
            return output, output == self.tokenizer.eos_token_id

        eos_index = (output[skip_tokens:] == self.tokenizer.eos_token_id).nonzero(as_tuple=False)
        if eos_index.nelement() > 0:
            return output[:eos_index[0].item() + skip_tokens + 1], True

        return output, False

    def decode_output(self, output):
        text = self.tokenizer.decode(output, skip_special_tokens=False)

        if self.config["SPACE_TOKEN_CHAR"] and output.numel() == 1:
            single_token = self.tokenizer.convert_ids_to_tokens([output], skip_special_tokens=False)[0]
            if single_token.startswith(self.config["SPACE_TOKEN_CHAR"]):
                text = ' ' + text

        return text

    def decode_outputs(self, outputs):
        decoded_outputs = []
        for output in outputs:
            decoded_output = self.decode_output(output)
            decoded_outputs.append(' ' if decoded_output == '' else decoded_output)

        return decoded_outputs

    def tokenize_prompt(self, prompt):
        encoded_dict = self.tokenizer.encode_plus(
            prompt,
            add_special_tokens=True,
            return_attention_mask=True,
            return_tensors='pt',
        ).to(self.device)

        return (
            encoded_dict["input_ids"],
            encoded_dict["attention_mask"]
        )

    def tokenize_prompts(self, prompts):
        encoded_dict = self.tokenizer.batch_encode_plus(
            prompts,
            add_special_tokens=True,
            return_attention_mask=True,
            return_tensors='pt',
            padding='longest',
        ).to(self.device)
        return (
            encoded_dict["input_ids"],
            encoded_dict["attention_mask"]
        )

    def extend_cache_mask(self, mask, attention_count, padding_count):
        return torch.cat((
            mask,
            torch.ones(attention_count, device=mask.device),
            torch.zeros(padding_count, device=mask.device)
        ), dim=0).to(self.device)

    def stack_masks(self, masks):
        return torch.stack(masks, dim=0).to(self.device)

    def generate_cache(self, tokens, attention_mask, past_key_values, config, streamer=None):
        if not self.isReady:
            raise NotReadyException("Model not ready.Please Use Model.load_model(path, config) and Model.run_model()")
        
        with torch.inference_mode():
            model_output = self.model.generate(
                input_ids=tokens,
                attention_mask=attention_mask if not past_key_values else None,
                past_key_values=past_key_values,
                use_cache=True,  # Ensure caching is enabled - HUGE performance hit on streaming tokens
                return_dict_in_generate=True,  # Return a dictionary containing past_key_values - required for use_cache
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,

                num_beams=int(config.get("num_beams", self.config["MODEL_DEFAULT_NUM_BEAMS"])),
                do_sample=bool(config.get("do_sample", self.config["MODEL_DEFAULT_DO_SAMPLE"])),
                temperature=float(config.get("temperature", self.config["MODEL_DEFAULT_TEMPERATURE"])),
                top_p=float(config.get("top_p", self.config["MODEL_DEFAULT_TOP_P"])),
                top_k=int(config.get("top_k", self.config["MODEL_DEFAULT_TOP_K"])),
                max_new_tokens=int(config.get("max_new_tokens", self.config["MODEL_DEFAULT_MAX_NEW_TOKENS"])),
                length_penalty=float(config.get("length_penalty", self.config["MODEL_DEFAULT_LENGTH_PENALTY"])),
                repetition_penalty=float(
                    config.get("repetition_penalty", self.config["MODEL_DEFAULT_REPETITION_PENALTY"])),

                streamer=streamer
            )

        if self.device == "cuda":
            torch.cuda.empty_cache()
        return model_output.sequences, model_output.get("past_key_values", None)
