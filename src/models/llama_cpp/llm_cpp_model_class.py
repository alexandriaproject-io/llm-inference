from logger import log
import torch
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

    def load_model(self):
        self.model = llama_cpp.Llama(model_path=self.model_path)

    def run_model(self):
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


        responses=[]
        if streamer:
            streamer.put(MockTensor(tokens, 2))
            stream = self.model(
                tokens.data,
                max_tokens=10000,
                stream=True,

            )
            for output in stream:
                texts=[]
                for choise in output["choices"]:
                    texts.append(choise["text"])

                streamer.put(MockTensor(texts, 1))



        return responses, None
