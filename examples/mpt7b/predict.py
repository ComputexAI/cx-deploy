# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import torch


MODEL_PATH = "./files"


class Predictor(BasePredictor):
    def setup(self):
        # Load Locally
        self.tokenizer = AutoTokenizer.from_pretrained(
            './files', trust_remote_code=True
        )

        config = AutoConfig.from_pretrained(MODEL_PATH, trust_remote_code=True)
        config.attn_config['attn_impl'] = 'triton'
        config.init_device = 'cuda:0'

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, config=config, local_files_only=True, trust_remote_code=True
        )

    def predict(
        self,
        prompt: str = Input(description="Code generation prompt"),
        max_length: int = Input(default=100, description="Maximum length of generated code"),
        top_p: float = Input(default=0.95, description="Top p value for sampling"),
        top_k: int = Input(default=4, description="Top k value for sampling"),
        temperature: float = Input(default=0.2, description="Temperature value for sampling"),
        num_return_sequences: int = Input(default=1, description="Number of sequences to return"),
    ) -> str:

        # Encode the input prompt and generate the attention mask
        encoded_prompt = self.tokenizer.encode(prompt)
        inputs = torch.tensor([encoded_prompt]).to(self.device)
        attention_mask = torch.ones(inputs.shape).to(self.device)

        # Generate output from the model
        result = self.model.generate(
            input_ids=inputs,
            attention_mask=attention_mask,
            max_length=max_length,
            do_sample=True,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        # Decode the generated output
        generated_code = self.tokenizer.decode(
            result[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        return generated_code
