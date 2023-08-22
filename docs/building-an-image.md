# Deploying a HuggingFace model to CX
Deploying your model to Computex (CX) allows you to leverage our infrastructure optimized for delivering the fastest serverless inference times. The deployment involves creating two Docker images: `model-download-image` and `model-run-image`. 

- The `model-download-image` solely contains the model which will be tensorized and stored on an attached NVMe SSD for exceptional model load times. 
- The `model-run-image` is a slim image carrying the necessary logic for executing inference.



## Model Download Image
This image creates the instruction set to download a tensorized model from HuggingFace

### Steps
1. Modify the `model_download.py` script to include the HuggingFace model you aim to download.
2. Once done, build and upload the image to your private CX Docker registry hosted at `registry.computex.ai`.

```
docker build -t registry.computex.ai/<org-name>/model-download-image-{MODEL-NAME}:v1 .
docker push registry.computex.ai/<org-name>/model-download-image-{MODEL-NAME}:v1
```

3. Deploy your model to CX using the CLI command:
```
cx deploy --app <app-name> --model-image registry.computex.ai/<org-name>/model-download-image-{MODEL-NAME}:v1 
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


## Model Run Image
Creating the model-run image involves including the logic necessary for running the model.

1. Update the code in load_model.py and predict.py based on your model's needs. Refer to your model's card in HuggingFace to ascertain which HuggingFace libraries you need to call.
2. Once done, package the image using Docker:
```
docker build -t registry.computex.ai/<org-name>/model-run-image-{MODEL-NAME}:v1 .
docker push registry.computex.ai/<org-name>/model-run-image-{MODEL-NAME}:v1
```
3. Deploy the model to CX using the CLI command and specify the --image flag. You should also define the GPU, number of CPU cores, and memory capacity:

```
cx deploy --app <app-name> --image registry.computex.ai/<org-name>/model-run-image-{MODEL-NAME}:v1 --gpu A40 --memory 16 --num-cpu-cores 8
```

# Next Steps
* [Deploying a model](deploying.md)
* [Running predictions on a model](predictions.md)
* [Deploying a virtual server](virtual-servers.md)