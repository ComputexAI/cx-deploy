from transformers import pipeline
import os

# Define the model and tokenizer repository ID on Hugging Face
model_repo = "openai/whisper-large-v2"
task = "automatic-speech-recognition"

# Define the paths where you want to store the model and tokenizer
model_path = "/mnt/model"
os.makedirs(model_path, exist_ok=True)

pipe = pipeline(task=task, model=model_repo)

# Set the image_processor to `None` to avoid an error when saving the model
pipe.image_processor = None

pipe.save_pretrained(model_path)
