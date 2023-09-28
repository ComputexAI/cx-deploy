import json
import logging
import torch

DEVICE = "cuda"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_model(config_path):
    with open(config_path, "r") as f:
        model_config = json.load(f)

    logger.info("model_config = ", model_config)
    model = torch.nn.Linear(10, 10)

    return model


def load_model(model_path: str):
    pretrained_model_path = f"{model_path}/model.tensors"
    config_path = f"{model_path}/config.json"

    model = setup_model(config_path)

    loaded_tensor = torch.load(pretrained_model_path)
    logger.info("Loaded tensor:", loaded_tensor)

    return model
