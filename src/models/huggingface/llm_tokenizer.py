import torch
from transformers import AutoTokenizer


class LLMTokenizer:
    def __init__(self, model_path, config):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
        self.tokenizer.pad_token = self.tokenizer.pad_token or self.tokenizer.bos_token
        self.tokenizer.add_special_tokens({"pad_token": self.tokenizer.pad_token})

        self.bos_token = self.tokenizer.bos_token
        self.eos_token = self.tokenizer.eos_token
        self.device = config.get("device", "cpu")
        self.SPACE_TOKEN_CHAR = config.get("SPACE_TOKEN_CHAR", None)

    def is_eos_token(self, token):
        return token == self.tokenizer.eos_token_id

    def cut_by_eos(self, output, skip_tokens=0):
        if output.numel() == 1:
            return output, output == self.tokenizer.eos_token_id

        eos_index = (output[skip_tokens:] == self.tokenizer.eos_token_id).nonzero(as_tuple=False)
        if eos_index.nelement() > 0:
            return output[:eos_index[0].item() + skip_tokens + 1], True

        return output, False

    def decode_output(self, output, skip_special_tokens=False):
        text = self.tokenizer.decode(output, skip_special_tokens)

        if self.SPACE_TOKEN_CHAR and output.numel() == 1:
            single_token = self.tokenizer.convert_ids_to_tokens([output], skip_special_tokens=False)[0]
            if single_token.startswith(self.SPACE_TOKEN_CHAR):
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
        )

        return encoded_dict

    def tokenize_prompts(self, prompts):
        encoded_dict = self.tokenizer.batch_encode_plus(
            prompts,
            add_special_tokens=True,
            return_attention_mask=True,
            return_tensors='pt',
            padding='longest',
        )
        return encoded_dict

    def extend_cache_mask(self, mask, attention_count, padding_count):
        return torch.cat((
            mask,
            torch.ones(attention_count, device=mask.device),
            torch.zeros(padding_count, device=mask.device)
        ), dim=0).to(self.device)

    def stack_masks(self, masks):
        if len(masks):
            return torch.stack(masks, dim=0).to(self.device)
        else:
            return torch.stack([])
