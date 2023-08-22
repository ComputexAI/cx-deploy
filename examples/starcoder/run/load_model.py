import time
import logging

import torch
from tensorizer import TensorDeserializer
from tensorizer.utils import convert_bytes, get_mem_usage, no_init_or_tensor
from transformers import AutoConfig, AutoModelForCausalLM

DEVICE = "cuda"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("load_model")
logger.info("starting load_model.py")

############################################
# Starcoder specific code


def get_token():
    token = ""
    with open("/transformer/huggingface_token", "r") as f:
        token = f.read()
    return token


TOKEN = get_token()
logger.info(f"TOKEN: {TOKEN}")

TOKEN = "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"
logger.info(f"TOKEN AFTER: {TOKEN}")

############################################


def load_model(model_name: str, model_path: str):
    """
    Loads the model using Tensorizer

    Args:
        model_name: unique name of the model
    """

    config = AutoConfig.from_pretrained(
        "bigcode/starcoder", trust_remote_code=True, use_auth_token=TOKEN
    )

    # This ensures that the model is not initialized.
    with no_init_or_tensor():
        model = AutoModelForCausalLM.from_config(
            config,
            trust_remote_code=True,
        )

    before_mem = get_mem_usage()

    # Lazy load the tensors from PVC into the model.
    start = time.time()
    # TODO: standardize how the model is being saved.
    # In this case, it is saved as "model.tensors" but for mpt7b it is saved
    # as "mpt7b-2.tensors"
    deserializer = TensorDeserializer(f"{model_path}/model.tensors", plaid_mode=True)
    deserializer.load_into_module(model)
    end = time.time()

    # Brag about how fast we are.
    total_bytes_str = convert_bytes(deserializer.total_tensor_bytes)
    duration = end - start
    per_second = convert_bytes(deserializer.total_tensor_bytes / duration)
    after_mem = get_mem_usage()
    deserializer.close()
    print(
        f"Deserialized {total_bytes_str} in {duration:0.2f}s, {per_second}/s"
        " using Tensorizer"
    )
    print(f"Memory usage before: {before_mem}")
    print(f"Memory usage after: {after_mem}")

    # Move model to CUDA if available
    if torch.cuda.is_available():
        model = model.to(DEVICE)
        print("Model moved to CUDA")
    else:
        print("CUDA not available")

    return model
