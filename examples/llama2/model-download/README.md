# Model Download Image

This image creates the instruction set to download a tensorized model from HuggingFace

## Instructions
Edit the `model_download.py` file to include the HuggingFace model repo you are trying to download.

Once complete, package and upload the image to a registry of choice. i.e.

```
docker build -t <your-registry>/<your-repo>/<image-name>:<tag> .
docker push <your-registry>/<your-repo>/<image-name>:<tag>
```

For example:
```
docker build -t registry.computex.ai/computex/model-llama2-13b-chat-hf:3 .
docker push registry.computex.ai/computex/model-llama2-13b-chat-hf:3
```

## Directory structure
Inside the container, the directory structure will be as follows:

```
/model_storage/model
    ├── config.json
    ├── model.tensors
    ├── special_tokens_map.json
    ├── tokenizer.json
    └── tokenizer_config.json
```


All models uploaded by your Org will be available in this volume.

## Usage

Build the image locally
```bash
docker build -t model-image .
```

## Debugging locally
To run the image locally and store the model in a local directory, run the following:

1. Create a `.secrets.json` file locally with the huggingface token stored
```json
{
  "huggingface_token": "token"
}
```

2. Create a local directory to store the model
```bash
mkdir local_model_directory
docker run -v local_model_directory:/mnt/model -v .secrets.json:/secrets/user/.secrets.json  model-image
```

3. Run the image locally and mount the local directory to the container
```bash
docker run -v local_model_directory:/mnt/model -v .secrets.json:/secrets/user/.secrets.json  model-image
```