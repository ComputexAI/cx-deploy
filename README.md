# CX Model Deployment
This repository provides a template for deploying an AI model for inference to our ComputeX (CX for short) Kuberentes backed Infrastructure. The template is designed to be easily customizable for your specific use case, requiring you to only modify a few sections of the code to insert your model and inference logic.

#### Prerequisites
- Docker
- Python 3.8 or higher

#### Repository Structure
The repository contains the following key files:

`app.py`: This file contains the FastAPI application. It defines the inference endpoint and how responses are handled.

`inference.py`: This is where you define your input model and inference logic. You should customize this file with your own model and inference processing logic.

`requirements.txt`: This file contains the Python packages that are required for your application to run.

`Dockerfile`: This file is used to build a Docker image of your application.

`/tests`: This directory contains a Python script and a Bash script that can be used to test your application locally.

#### How to Use
1. Clone this repository to your local machine.
2. Modify the `inference.py` file to include your specific AI model and inference logic. There are comments throughout the file guiding you on where to put your code.
3. Add Python dependencies to `requirements.txt`
4. Add System dependencies to `Dockerfile` in the commented out section.
5. Build and run the application locally to test your changes.

#### Running Locally on Linux x86 devices
To build and run the application locally, run the following commands in the root directory:

```
docker build -t my-model-inference:my-tag .
docker run -p 8000:8000 my-model-inference:my-tag
```

You should now have a FastAPI application running at http://localhost:8000 that will run inference on your model when the /infer endpoint is hit with a POST request.

#### Running Locally with ARM devices (i.e. M1 Mac)
```
docker buildx create --name my-builder
docker buildx use my-builder
docker buildx build --platform linux/amd64,linux/arm64 -t my-model-inference:my-tag .
docker run -p 8000:8000 my-model-inference:my-tag
```

#### Running Tests
Once the container is running, open a second terminal to send requests to the API
```
  curl -X 'POST' \
    'http://localhost:8000/infer' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'input_file=@README.md;type=audio/mpeg' \
    -F 'params=[{"name":"model_name", "value":"tiny"}, {"name":"input_type", "value":"text_input"}]'
```

#### Deployment
When you are complete, push the container to your Dockerhub container registry account. You can do this by running the following commands:

```
docker push <your-username>/<your-container-name>:<your-container-tag>
```

You can then deploy the container to a CX cluster by running the following command:

```
export CX_API_KEY=<your-api-key>

curl -X 'POST' \
  'https://api.computex.co/api/v1/deployments/deploy' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $CX_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "app_name": "<your-app-name>",
  "container_image": "<your-username>/<your-container-name>:<your-container-tag>",
  "num_cpu_cores": 1,
  "num_gpu": 0,
  "gpu_sku": "A40",
  "cpu_sku": "intel_xeon_v3",
  "memory": 4,
  "region": "LGA1",
  "replicas": 1
}'
```
Update the payload in `-d` to match your desired deployment configuration.


#### Run Inference on the Deployed Model
```
export CX_API_KEY=<your-api-key>

curl -X 'POST' \
  'https://api.computex.co/api/v1/deployments/template-03db38d/infer' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $CX_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_file=@<filename-to-upload>;type=<mime type>' \
  -F 'params=[{"name":"<your-param-name>", "value":"<your-param-value>"}, {"name":"<your-param-name>", "value":"<your-param-value>"}]'
```
Update the payload in `-F` to match your desired inference configuration. 

#### Support
If you have any issues or questions regarding how to use this template, reach out to abate@computex.co.
