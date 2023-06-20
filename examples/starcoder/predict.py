# Prediction interface for Cog :gear:
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input
from typing import Any
from transformers import AutoModelForCausalLM, AutoTokenizer


checkpoint = "./files"
device = "cuda"


class Predictor(BasePredictor):
    def setup(self):
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        self.model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

    def predict(
        self,
        prompt: str = Input(description="Code prompt"),
        max_length: int = Input(default=100, description="Maximum length of generated code"),
        top_p: float = Input(default=0.95, description="Top p value for sampling"),
        top_k: int = Input(default=50, description="Top k value for sampling"),
        temperature: float = Input(default=0.2, description="Temperature value for sampling"),
        num_return_sequences: int = Input(default=1, description="Number of sequences to return"),
    ) -> Any:
        """Run a single prediction on the model"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(device)
        result = self.model.generate(
            inputs,
            max_length=max_length,
            do_sample=True,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
        )
        return result
