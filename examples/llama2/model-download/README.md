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
docker build -t registry.computex.ai/MyOrg/model-storage-mpt-7b:1 .
docker push registry.computex.ai/MyOrg/model-storage-mpt-7b:1
```

## Directory structure
Inside the container, the directory structure will be as follows:

```
/mnt
    └── {model_name}
        ├── pretrained_tokenizer
        ├── {model_name}
        └── {model_name}.tensors
```

For example:
```
/mnt
    ├── mpt-7b
    │   ├── pretrained_tokenizer
    │   ├── mpt-7b
    │   └── mpt-7b.tensors
    └── starcoder
        ├── pretrained_tokenizer
        ├── starcoder
        └── starcoder.tensors
```

All models uploaded by your Org will be available in this volume.

## Usage

Build the image locally
```bash
docker build -t model-image .
```

Run the image locally and store the model in a local directory
```bash
mkdir /path/to/local/directory/to/store/model
docker run -v /path/to/local/directory/to/store/model:/mnt/model -v /path/to/huggingface_token:/secrets/user/huggingface_token  model-image
```