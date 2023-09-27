import json
import time
import logging

from tensorizer import TensorDeserializer
from tensorizer.utils import convert_bytes, get_mem_usage, no_init_or_tensor

# Make sure you are importing the right type!
from transformers import AutoConfig, AutoModelForCausalLM

DEVICE = "cuda"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_model(config_path):
    """with open(config_path, "r") as f:
    model_config = json.load(f)"""

    config = AutoConfig.from_pretrained(config_path)

    # This ensures that the model is not initialized.
    with no_init_or_tensor():
        model = AutoModelForCausalLM.from_config(config)

    return model


def load_model(model_path: str):
    """
    Loads the model using Tensorizer

    Args:
        model_path: Path to the model & config files
    """
    pretrained_model_path = f"{model_path}/model.tensors"
    config_path = f"{model_path}/config.json"

    model = setup_model(config_path)

    before_mem = get_mem_usage()
    start = time.time()

    # Lazy load the tensors from PVC into the model.
    # Set plaid_mode to True to cut down on load times significantly.
    deserializer = TensorDeserializer(pretrained_model_path, plaid_mode=True)
    deserializer.load_into_module(model)

    end = time.time()
    after_mem = get_mem_usage()

    total_bytes_str = convert_bytes(deserializer.total_tensor_bytes)
    duration = end - start
    per_second = convert_bytes(deserializer.total_tensor_bytes / duration)

    deserializer.close()

    # Print stats from model loading
    logger.info(f"Deserialized {total_bytes_str} in {duration:0.2f}s, {per_second}/s")
    logger.info(f"Memory usage before: {before_mem}")
    logger.info(f"Memory usage after: {after_mem}")

    return model
