from transformers import AutoModelForCausalLM, AutoTokenizer
from logger import log
import torch


class LLMModel:
    def __init__(self, model_path, config):
        self.tokenizer = None
        self.model = None
        self.config = config
        self.model_path = model_path
        self.device = "cuda" if self.config["ENABLE_CUDA"] and torch.cuda.is_available() else "cpu"
        self.isBF16Supported = False if not self.config["ENABLE_CUDA"] else torch.cuda.is_bf16_supported()
        self.isQuantized = self.config["LOAD_IN_8BIT"]
        self.model_type = torch.bfloat16 if self.isBF16Supported else torch.float16

    def load_model(self):
        log.info(f"Target model: {self.model_path} using seed {self.config['MODEL_SEED']}")
        torch.cuda.manual_seed(self.config["MODEL_SEED"])
        torch.manual_seed(self.config["MODEL_SEED"])
        log.info("Loading model from disk. Be patient this can take a while...")

        low_mem_mode = self.isQuantized or self.config["LOW_CPU_MEM_USAGE"]
        device_map = None
        if low_mem_mode:
            device_map = 'cpu' if self.device == 'cpu' else self.config["TARGET_GPU_INDEX"]

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            return_dict=True,
            load_in_8bit=self.isQuantized,
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
        log.info(f"Model is ready to go.")
