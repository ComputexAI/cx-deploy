import json
import logging
import os
from typing import Optional, Union

import torch
from diffusers import (
    ConfigMixin,
)
from transformers import (
    AutoConfig,
    LlamaForCausalLM,
    AutoTokenizer,
    LlamaConfig,
)

from tensorizer import TensorSerializer, utils


def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    fh = logging.StreamHandler()
    fh_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s(%(process)d) - %(message)s"
    )
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger


logger = logging.getLogger(__name__)

logger = setup_logging()


def get_token(token_path="/secrets/user/.secrets.json"):
    """Load the huggingface token from the secrets volume.

    To deploy this secret through the CX API, include the Huggingface
    token in the `secrets` field of the deploy request.

    An example payload to the `/deploy` endpoint:

    {
    "app_name": "llama2",
    "container_image": "registry.computex.ai/computex/predict-llama2-13b-chat-hf:1",
    "model_image": "registry.computex.ai/computex/model-llama2-13b-chat-hf:3",
    "num_cpu_cores": 10,
    "num_gpu": 1,
    "gpu_sku": "A40",
    "memory": 64,
    "container_concurrency": 1,
    "min_scale": 0,
    "max_scale": 1,
    "secrets": {"huggingface_token": "my-secret-token"},
    "is_public": false
    }
    """

    with open(token_path, "r") as token_path:
        data = json.load(token_path)

    token = data["huggingface_token"]

    return token


def serialize_model(
    model: torch.nn.Module,
    config: Optional[Union[ConfigMixin, AutoConfig, dict]],
    model_directory: str,
):
    """
    Remove the tensors from a PyTorch model, convert them to NumPy
    arrays and serialize them to GooseTensor format. The stripped
    model is also serialized to pytorch format.

    Args:
        model: The model to serialize.
        config: The model's configuration. This is optional and only
            required for HuggingFace Transformers models. Diffusers
            models do not require this.
        model_directory: The directory to save the serialized model to.
        model_prefix: The prefix to use for the serialized model files. This
            is purely optional, and it allows for multiple models to be
            serialized to the same directory. A good example are Stable
            Diffusion models. Default is "model".
    """

    os.makedirs(model_directory, exist_ok=True)
    logger.info(f"Serializing model to {model_directory}")

    if config is None:
        config = model

    if config is not None:
        if isinstance(config, LlamaConfig):
            config.to_json_file(f"{model_directory}/config.json")

        if isinstance(config, dict):
            with open(f"{model_directory}/config.json", "w") as config_file:
                config_file.write(json.dumps(config, indent=2))

    ts = TensorSerializer(f"{model_directory}/model.tensors")
    ts.write_module(model)
    ts.close()


def hf_main(input_directory, output_prefix):
    """Serialize models from HuggingFace Transformers.

    https://github.com/huggingface/transformers
    """
    token = get_token()

    dtype = torch.float16
    model_config = LlamaConfig.from_pretrained(input_directory, token=token)

    model = LlamaForCausalLM.from_pretrained(
        input_directory,
        config=model_config,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
        token=token,
    )

    logger.info("Serializing model")
    logger.info("GPU: " + utils.get_gpu_name())
    logger.info("PYTHON USED RAM: " + utils.get_mem_usage())

    serialize_model(model=model, config=model_config, model_directory=output_prefix)

    tokenizer = AutoTokenizer.from_pretrained(input_directory, token=token)
    tokenizer.save_pretrained(output_prefix)
    logger.info("Done")


if __name__ == "__main__":
    hf_main(
        input_directory="meta-llama/Llama-2-13b-chat-hf", output_prefix="/mnt/model"
    )
