import gc
import json
import logging
import os
import tempfile
import time
from typing import Optional, Type, Union

import torch
from diffusers import (
    AutoencoderKL,
    ConfigMixin,
    LMSDiscreteScheduler,
    ModelMixin,
    StableDiffusionPipeline,
    UNet2DConditionModel,
)
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    CLIPTextConfig,
    CLIPTextModel,
    PretrainedConfig,
    PreTrainedModel,
    AutoModelForSeq2SeqLM,
)

from tensorizer import TensorDeserializer, TensorSerializer, stream_io, utils


def get_token():
    token = ""
    with open("/src/huggingface_token", "r") as f:
        token = f.read()
    return token


TOKEN = get_token()


# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


def serialize_model(
    model: torch.nn.Module,
    config: Optional[Union[ConfigMixin, AutoConfig, dict]],
    model_directory: str,
    model_prefix: str = "model",
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
    dir_prefix = f"{model_directory}/{model_prefix}"
    logger.info(f"Serializing model to {dir_prefix}")

    if config is None:
        config = model
    if config is not None:
        if hasattr(config, "to_json_file"):
            config.to_json_file(f"{dir_prefix}-config.json")
        if isinstance(config, dict):
            with open(f"{dir_prefix}-config.json", "w") as config_file:
                config_file.write(json.dumps(config, indent=2))

    ts = TensorSerializer(f"{dir_prefix}.tensors")
    ts.write_module(model)
    ts.close()


def load_model(
    path_uri: str,
    model_class: Union[
        Type[PreTrainedModel], Type[ModelMixin], Type[ConfigMixin]
    ],
    config_class: Optional[
        Union[Type[PretrainedConfig], Type[ConfigMixin], Type[AutoConfig]]
    ] = None,
    model_prefix: Optional[str] = "model",
    device: torch.device = utils.get_device(),
    dtype: Optional[str] = None,
) -> torch.nn.Module:
    """
    Given a path prefix, load the model with a custom extension

    Args:
        path_uri: path to the model. Can be a local path or a URI
        model_class: The model class to load the tensors into.
        config_class: The config class to load the model config into. This must be
            set if you are loading a model from HuggingFace Transformers.
        model_prefix: The prefix to use to distinguish between multiple serialized
            models. The default is "model".
        device: The device onto which to load the model.
        dtype: The dtype to load the tensors into. If None, the dtype is inferred from
            the model.
    """

    if model_prefix is None:
        model_prefix = "model"

    begin_load = time.time()
    ram_usage = utils.get_mem_usage()

    config_uri = f"{path_uri}/{model_prefix}-config.json"
    tensors_uri = f"{path_uri}/{model_prefix}.tensors"
    tensor_stream = stream_io.open_stream(tensors_uri)

    logger.info(f"Loading {tensors_uri}, {ram_usage}")

    tensor_deserializer = TensorDeserializer(
        tensor_stream, device=device, dtype=dtype, lazy_load=True
    )

    if config_class is not None:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_config_path = os.path.join(temp_dir, "config.json")
                with open(temp_config_path, "wb") as temp_config:
                    temp_config.write(stream_io.open_stream(config_uri).read())
                config = config_class.from_pretrained(temp_dir)
                config.gradient_checkpointing = True
        except ValueError:
            config = config_class.from_pretrained(config_uri)
        with utils.no_init_or_tensor():
            # AutoModels instantiate from a config via their from_config()
            # method, while other classes can usually be instantiated directly.
            config_loader = getattr(model_class, "from_config", model_class)
            model = config_loader(config)
    else:
        try:
            config = json.loads(
                stream_io.open_stream(config_uri).read().decode("utf-8")
            )
        except ValueError:
            with open(config_uri, "r") as f:
                config = json.load(f)
        with utils.no_init_or_tensor():
            model = model_class(**config)

    tensor_deserializer.load_into_module(model)

    tensor_load_s = time.time() - begin_load
    rate_str = utils.convert_bytes(
        tensor_deserializer.total_bytes_read / tensor_load_s
    )
    tensors_sz = utils.convert_bytes(tensor_deserializer.total_bytes_read)
    logger.info(
        f"Model tensors loaded in {tensor_load_s:0.2f}s, read "
        f"{tensors_sz} @ {rate_str}/s, {utils.get_mem_usage()}"
    )

    return model


def df_main(input_directory, output_prefix, validate) -> None:
    """Serialize models from HuggingFace Diffusers.

    https://github.com/huggingface/diffusers
    """
    output_prefix = output_prefix

    hf_api_token = os.environ.get("HF_API_TOKEN")

    pipeline = StableDiffusionPipeline.from_pretrained(
        input_directory, use_auth_token=hf_api_token
    )

    logger.info("Serializing model")
    logger.info("GPU: " + utils.get_gpu_name())
    logger.info("PYTHON USED RAM: " + utils.get_mem_usage())

    serialize_model(
        pipeline.text_encoder.eval(),
        pipeline.text_encoder.config,
        output_prefix,
        "encoder",
    )
    serialize_model(pipeline.vae.eval(), None, output_prefix, "vae")
    serialize_model(pipeline.unet.eval(), None, output_prefix, "unet")

    pipeline.tokenizer.save_pretrained(output_prefix)
    pipeline.scheduler.save_pretrained(output_prefix)

    if validate:
        del pipeline
        gc.collect()
        device = utils.get_device()

        logger.info("Validating serialization")
        vae = load_model(output_prefix, AutoencoderKL, None, "vae", device)
        unet = load_model(
            output_prefix, UNet2DConditionModel, None, "unet", device
        )
        encoder = load_model(
            output_prefix, CLIPTextModel, CLIPTextConfig, "encoder", device
        )

        pipeline = StableDiffusionPipeline(
            text_encoder=encoder,
            vae=vae,
            unet=unet,
            tokenizer=AutoTokenizer.from_pretrained(
                input_directory, subfolder="tokenizer"
            ),
            scheduler=LMSDiscreteScheduler.from_pretrained(
                input_directory, subfolder="scheduler"
            ),
            safety_checker=None,
            feature_extractor=None,
            requires_safety_checker=False,
        ).to(device)

        prompt = "a photo of an astronaut riding a horse on mars"
        with torch.autocast(device.type):
            pipeline(prompt).images[0].save("test.png")
    logger.info("Done")


def hf_main(input_directory, output_prefix, validate):
    """Serialize models from HuggingFace Transformers.

    https://github.com/huggingface/transformers
    """
    output_prefix = output_prefix

    dtype = torch.float16

    model_config = AutoConfig.from_pretrained(
        input_directory, trust_remote_code=True, use_auth_token=TOKEN
    )
    model = AutoModelForCausalLM.from_pretrained(
        input_directory,
        config=model_config,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
        use_auth_token=TOKEN,
    )

    logger.info("Serializing model")
    logger.info("GPU: " + utils.get_gpu_name())
    logger.info("PYTHON USED RAM: " + utils.get_mem_usage())

    serialize_model(
        model=model, config=model_config, model_directory=output_prefix
    )

    tokenizer = AutoTokenizer.from_pretrained(
        input_directory, use_auth_token=TOKEN
    )
    tokenizer.save_pretrained(output_prefix)

    if validate:
        del model, model_config
        gc.collect()
        device = utils.get_device()
        logger.info("Validating serialization")
        model = load_model(
            output_prefix,
            AutoModelForSeq2SeqLM,
            AutoConfig,
            None,
            device,
            dtype,
        ).eval()
        # test generation
        eos = tokenizer.eos_token_id
        input_code = "def print_hello_world():"
        encoding = tokenizer(input_code, return_tensors="pt").to(device)
        encoding['decoder_input_ids'] = encoding['input_ids'].clone()
        with torch.no_grad():
            output = model.generate(
                **encoding, max_length=50, do_sample=True, pad_token_id=eos
            )
        logger.info(
            "Test Output:"
            f" {tokenizer.decode(output[0], skip_special_tokens=True)}"
        )
    logger.info("Done")


def main(model_type: str = "transformers", input_directory: str = None, output_prefix: str = None, validate: bool = False):

    if model_type == "transformers":
        hf_main(input_directory, output_prefix, validate)
    elif model_type == "diffusers":
        df_main(input_directory, output_prefix, validate)
    else:
        raise ValueError(
            f"Unknown model type {model_type} (transformers or diffusers)"
        )


if __name__ == "__main__":
    main(
        model_type="transformers",
        input_directory="bigcode/starcoder",
        output_prefix="/mnt/starcoder",
        validate=False
    )
