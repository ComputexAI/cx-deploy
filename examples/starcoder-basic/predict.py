from cog import BasePredictor, Input
from typing import Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

DEVICE = "cuda"


def get_token():
    token = ""
    with open("/src/huggingface_token", "r") as f:
        token = f.read()
    return token


TOKEN = get_token()


class Predictor(BasePredictor):
    def setup(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "bigcode/starcoder", use_auth_token=TOKEN
        )

        """ 
        # Load the model in 16 bit precision
        self.model = AutoModelForCausalLM.from_pretrained(
            "bigcode/starcoder",
            use_auth_token=TOKEN,
            device_map="auto",
            torch_dtype=torch.float16,
        ) """

        # Load the model in 32 bit precision
        self.model = AutoModelForCausalLM.from_pretrained(
            "bigcode/starcoder", use_auth_token=TOKEN, device_map="auto"
        )

        print(f"Memory footprint: {self.model.get_memory_footprint() / 1e6:.2f} MB")

    def predict(
        self,
        prompt: str = Input(description="Code prompt"),
        max_length: int = Input(
            default=100, description="Maximum length of generated code"
        ),
        top_p: float = Input(default=0.95, description="Top p value for sampling"),
        top_k: int = Input(default=50, description="Top k value for sampling"),
        temperature: float = Input(
            default=0.2, description="Temperature value for sampling"
        ),
        num_return_sequences: int = Input(
            default=1, description="Number of sequences to return"
        ),
    ) -> Any:
        """Run a single prediction on the model"""

        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)

        result = self.model.generate(
            inputs,
            max_length=max_length,
            do_sample=True,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
        )

        # Decode the generated output
        generated_code = self.tokenizer.decode(
            result[0], skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return generated_code
