import torch
from src.models.llama_cpp.utils import MockTensor


# This is a mock tokenizer to not rewrite existing server code that is purpose built for GPU inference
class LLMCPPTokenizer:

    def is_eos_token(self, token):
        return token == self.tokenizer.eos_token_id

    def cut_by_eos(self, output, skip_tokens=0):
        if output.numel() == 1:
            return output, output == self.tokenizer.eos_token_id

        eos_index = (output[skip_tokens:] == self.tokenizer.eos_token_id).nonzero(as_tuple=False)
        if eos_index.nelement() > 0:
            return output[:eos_index[0].item() + skip_tokens + 1], True

        return output, False

    def decode_output(self, output):
        return output

    def decode_outputs(self, outputs):
        return outputs

    def tokenize_prompts(self, prompts):
        return {
            "input_ids": MockTensor(prompts),
            "attention_mask": MockTensor([])
        }
