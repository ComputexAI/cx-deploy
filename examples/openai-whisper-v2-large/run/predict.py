from typing import Dict
import logging
import os
import torch
import time
from transformers import pipeline
from fastapi import FastAPI, Depends
import requests
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import mimetypes

app = FastAPI()
MODEL_NAME = "whisper-large-v2"
MODEL_PATH = "/model_storage/model"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(MODEL_NAME)
logger.info(f"Model Name: {MODEL_NAME}")


@app.on_event("startup")
async def startup_event():
    logger.info("Contents of Docker container:")
    os.system("ls -R /app/")
    logger.info("Contents of model storage:")
    os.system("ls -R /model_storage/")
    model = Model(MODEL_NAME)
    model.load()
    app.state.model = model


def model_is_ready(app: FastAPI = Depends()):
    return app.state.model.ready


class Timer:
    def __init__(self, logger):
        self.logger = logger
        self.start_time = time.time()
        self.last_checkpoint = self.start_time

    def checkpoint(self, name):
        now = time.time()
        elapsed = now - self.last_checkpoint
        self.last_checkpoint = now
        self.logger.info(f"{name} took: {elapsed:.3f} seconds")

    def total(self):
        total_elapsed = time.time() - self.start_time
        self.logger.info(f"Total time: {total_elapsed:.3f} seconds")


class Model:
    def __init__(self, name: str):
        self.name = name
        self.tokenizer = None
        self.pipe = None
        self.eos = None
        self.ready = False

    def load(self):
        logger.info(f"Loading {MODEL_NAME}")
        timer = Timer(logger)
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=MODEL_PATH,
            tokenizer=MODEL_PATH,
            chunk_length_s=30,
            device=0,
        )
        self.ready = True
        timer.checkpoint("Loading model")
        timer.total()

    def validate(self, payload: Dict):
        # Ensure that the request has the appropriate type to process
        if not isinstance(payload, Dict):
            raise Exception("Expected payload to be a dict")

    def download_audio_file(self, url: str):
        # Download audio from URL
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download audio from URL: {url}")

        # Parse the URL to get the file extension
        parsed_url = urlparse(url)
        path = parsed_url.path
        suffix = os.path.splitext(path)[1]
        if not suffix:
            # If no suffix is found, guess the file type from the URL content
            response = requests.head(url)
            content_type = response.headers.get("content-type")
            if not content_type:
                raise Exception(
                    f"Failed to determine file type from URL: {url} and no suffix was found"
                )

            suffix = mimetypes.guess_extension(content_type)

        # Save the audio file to a temporary file
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(response.content)
            tmp_filename = tmp.name
        return tmp_filename

    def predict(self, payload: Dict) -> Dict:
        logger.info("Starting prediction")

        if not self.pipe:
            logger.error("Pipe not loaded")
            raise Exception("Pipe not loaded")

        timer = Timer(logger)

        # Download audio from URL
        url = payload.get("url", None)
        if not url:
            raise Exception("Please provide a URL")
        audio_path = self.download_audio_file(url)
        timer.checkpoint("Download audio")

        # Model prediction
        return_timestamps = payload.get("return_timestamps", False)

        with torch.no_grad():
            prediction = self.pipe(
                audio_path, batch_size=8, return_timestamps=return_timestamps
            )
        timer.checkpoint("Model prediction")

        timer.total()

        # Clean up the temporary file
        os.remove(audio_path)
        timer.checkpoint("Clean up temporary file")

        return {"predictions": prediction}


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
