import json
import logging
import os


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


def save_files_to_volume(model_directory: str):
    os.makedirs(model_directory, exist_ok=True)
    logger.info(f"Serializing model to {model_directory}")
    config = {"test-config": "test-config-value"}

    with open(f"{model_directory}/config.json", "w") as config_file:
        config_file.write(json.dumps(config, indent=2))


if __name__ == "__main__":
    save_files_to_volume(model_directory="/mnt/model")
