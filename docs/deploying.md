# Deploying to CX


## Command Line Interface
The `cx` CLI is the easiest and fastest way to deploy models to CX. 

First, login to cx

```bash
$ cx login --username {username} --password {password}
```

Next, push the image to a private registry.

```bash
$ cx push <image>:<tag>
```

Finally, deploy the model to CX infrastructure

```bash
$ cx deploy --app-name=<app> --container-image=<image> --gpu=<GPU model> --num-cpu=<num cpu cores> --memory=<RAM in GB> --replicas=<# of Replicas>
```

## Available GPUs:
Choose from the following GPU models
- H100_NVLINK_80GB
- A100_NVLINK_80GB
- A100_NVLINK
- A100_PCIE_40GB
- A100_PCIE_80GB
- A40
- RTX_A6000
- RTX_A5000
- RTX_A4000
- Tesla_V100_NVLINK
- Quadro_RTX_5000
- Quadro_RTX_4000


## cURL Requests
If you need maximum flexibility to execute this anywhere, use the following curl request to deploy a model.
```console
$ curl -X 'POST' \
  'https://api.computex.co/api/v1/deployments/deploy' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your-token-generated-from-login>' \
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

Add the token generated from the login step in the `Authorization` header.

# Next Steps
* [Running predictions on a model](predictions.md)