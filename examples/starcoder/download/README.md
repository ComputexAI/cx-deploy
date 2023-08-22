## Model Download Image
This image creates the instruction set to download a tensorized model from HuggingFace

### Steps
1. Modify the `model_download.py` script to include the HuggingFace model you aim to download.
2. Once done, build and upload the image to your private CX Docker registry hosted at `registry.computex.ai`.

```
docker build -t registry.computex.ai/<org-name>/model-download-image:v1 .
docker push registry.computex.ai/<org-name>/model-download-image:v1
```

3. Deploy your model to CX using the CLI command:
```
cx deploy --app <app-name> --model-image registry.computex.ai/<org-name>/model-download-image:v1 
```

### Directory structure
Inside the container, the directory structure will be as follows:

```
/mnt
    └── {model_name}
        ├── pretrained_tokenizer
        ├── {model_name}
        └── {model_name}.tensors
```

Each app gets its own Persistent Volume ensuring exceptionally fast bootup times.
