import logging
import os
import time
from typing import Dict
from fastapi import FastAPI, Depends
import torch
from transformers import AutoTokenizer

import load_model

app = FastAPI()

MODEL_NAME = "model"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(MODEL_NAME)
logger.info(f"Model Name: {MODEL_NAME}")


@app.on_event("startup")
async def startup_event():
    logger.info("Contents of Docker container:")
    os.system("ls -R /model_storage/")
    model = Model(MODEL_NAME)
    model.load()
    app.state.model = model


def model_is_ready(app: FastAPI = Depends()):
    return app.state.model.ready


class Model:
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.tokenizer = None
        self.eos = None
        self.ready = False
        self.model_path = "/model_storage/model"

    def load(self):
        logger.info(f"Loading {MODEL_NAME}")

        self.model = load_model.load_model(self.model_path)

        self.model.eval()
        torch.manual_seed(100)

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, trust_remote_code=True
        )
        self.eos = self.tokenizer.eos_token_id

        self.ready = True

    def validate(self, payload: Dict):
        # Ensure that the request has the appropriate type to process
        if not isinstance(payload, Dict):
            raise Exception("Expected payload to be a dict")

    def predict(self, payload: Dict) -> Dict:
        logger.info("starting prediction")

        # Ensure certain defaults if not provided by the user.
        payload.setdefault("prompt", ["Please input some text"])
        payload.setdefault("max_length", 4096)
        payload.setdefault("top_p", 0.95)
        payload.setdefault("top_k", 1)
        payload.setdefault("temperature", 0.2)
        payload.setdefault("num_return_sequences", 1)

        # Extract the prompt and remove from payload
        prompt = payload.pop("prompt")
        if isinstance(prompt, str):
            prompt = [prompt]

        model_on_gpu = next(self.model.parameters()).device
        logger.info(f"model running on GPU or CPU: {model_on_gpu}")

        outputs = []
        for text in prompt:
            input_ids = self.tokenizer.encode(text, return_tensors="pt").to("cuda")

            with torch.no_grad():
                start_time = time.time()
                output_ids = self.model.generate(input_ids, **payload)
                duration = time.time() - start_time
                logger.info(f"Model output generated in {duration:0.2f} seconds")

            output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            outputs.append(output)

        return {"predictions": outputs}


@app.get("/ready")
async def ready():
    return {"ready": app.state.model.ready}


@app.post("/predict")
async def predict(payload: Dict):
    app.state.model.validate(payload)
    try:
        return app.state.model.predict(payload)
    except Exception as e:
        return {"error": str(e)}


@app.post("/terminate")
async def terminate():
    logger.info("Terminating server")
    successful_exit_status = 0
    os._exit(successful_exit_status)
