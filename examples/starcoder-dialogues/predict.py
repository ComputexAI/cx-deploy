from cog import BasePredictor, Input
from typing import Any
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, set_seed
import torch
import json

from dialogues import DialogueTemplate, get_dialogue_template


DEVICE = "cuda"
MODEL_ID = "bigcode/starcoder"


def get_token():
    token = ""
    with open("/src/huggingface_token", "r") as f:
        token = f.read()
    return token


TOKEN = get_token()


class Predictor(BasePredictor):
    def setup(self):
        set_seed(42)

        try:
            self.dialogue_template = DialogueTemplate.from_pretrained(
                MODEL_ID, revision=None, use_auth_token=TOKEN
            )
        except Exception:
            print(
                "No dialogue template found in model repo. ",
                "Defaulting to the `no_system` template.",
            )
            self.dialogue_template = get_dialogue_template("no_system")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID, revision=None, use_auth_token=TOKEN
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            revision=None,
            use_auth_token=TOKEN,
            # load_in_8bit=True,
            device_map="auto",
            # torch_dtype=torch.float16,
        )

        memory_footprint = self.model.get_memory_footprint()
        print(f"Memory footprint: {memory_footprint / 1e6:.2f} MB")

    def predict(
        self,
        prompt: str = Input(description="Batch of code prompts"),
        top_p: float = Input(default=0.95, description="Top p value for sampling"),
        top_k: int = Input(default=50, description="Top k value for sampling"),
        temperature: float = Input(
            default=0.2, description="Temperature value for sampling"
        ),
    ) -> Any:
        """Run a prediction using the 16-bit Starcoder model.

        Based off of the following example:
        https://github.com/bigcode-project/starcoder/blob/main/chat/generate.py

        The input prompt is automatically formatted to enhance the model's
        performance. The output includes the formatted input prompt
        along with the response generated by the model.
        """
        self.dialogue_template.messages = [json.loads(prompt)]
        formatted_prompts = [self.dialogue_template.get_inference_prompt()]

        generation_config = GenerationConfig(
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.convert_tokens_to_ids(
                self.dialogue_template.end_token
            ),
            min_new_tokens=32,
            max_new_tokens=256,
        )
        batch = self.tokenizer(
            formatted_prompts, return_tensors="pt", return_token_type_ids=False
        ).to(DEVICE)

        generated_ids = self.model.generate(
            **batch, generation_config=generation_config
        )

        generated_text = self.tokenizer.decode(
            generated_ids[0], skip_special_tokens=False
        ).lstrip()

        print(generated_text)
        return generated_text
