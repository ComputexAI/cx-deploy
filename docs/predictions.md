# Running Inference

Run inference on models deployed on the CX platform. You can run inference on models you uploaded yourself, or publicly available ones hosted by CX. 


```console
cx predict --help                                                                   
Usage: cx predict [OPTIONS]

Options:
  --app TEXT
  --data TEXT
  --is-public BOOLEAN
  --is-serverless BOOLEAN
  --help    Show this message and exit.
```

You can then deploy the container to a CX cluster by running the following command:

```console
$ export CX_API_KEY=<your-api-key>

$ curl -X 'POST' \
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


## Run Inference on the Deployed Model

```console
$ export CX_API_KEY=<your-api-key>

$ curl -X 'POST' \
  'https://api.computex.co/api/v1/deployments/template-03db38d/infer' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $CX_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_file=@<filename-to-upload>;type=<mime type>' \
  -F 'params=[{"name":"<your-param-name>", "value":"<your-param-value>"}, {"name":"<your-param-name>", "value":"<your-param-value>"}]'
```
Update the payload in `-F` to match your desired inference configuration. 
