import time
import logging

import torch
from tensorizer import TensorDeserializer
from tensorizer.utils import convert_bytes, get_mem_usage, no_init_or_tensor
from transformers import AutoConfig, AutoModelForSeq2SeqLM

DEVICE = "cuda"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("load_model")
logger.info("starting load_model.py")


def load_model(model_name: str, model_path: str):
    """
    Loads the model using Tensorizer

    Args:
        model_name: unique name of the model
    """

    config = AutoConfig.from_pretrained(
        "Salesforce/codet5p-16b", trust_remote_code=True
    )

    # This ensures that the model is not initialized.
    with no_init_or_tensor():
        model = AutoModelForSeq2SeqLM.from_config(
            config,
            trust_remote_code=True,
        )

    before_mem = get_mem_usage()

    # Lazy load the tensors from PVC into the model.
    start = time.time()
    model_full_path = f"{model_path}/model.tensors"
    deserializer = TensorDeserializer(model_full_path, plaid_mode=True)
    deserializer.load_into_module(model)
    end = time.time()

    # Brag about how fast we are.
    total_bytes_str = convert_bytes(deserializer.total_tensor_bytes)
    duration = end - start
    per_second = convert_bytes(deserializer.total_tensor_bytes / duration)
    after_mem = get_mem_usage()
    deserializer.close()
    logger.info(
        f"Deserialized {total_bytes_str} in {duration:0.2f}s, {per_second}/s"
        " using Tensorizer"
    )
    logger.info(f"Memory usage before: {before_mem}")
    logger.info(f"Memory usage after: {after_mem}")

    # Move model to CUDA if available
    if torch.cuda.is_available():
        model = model.to(DEVICE)
        logger.info("Model moved to CUDA")
    else:
        logger.info("CUDA not available")

    return model
