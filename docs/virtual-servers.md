# Deploying a virtual server
Deploy a virtual server with SSH access for full flexibility.

A full example in python can be found [here](/api/deploy_virtual_server.py)

## Authenticate to the API
Authenticate to the API to generate the necessary headers

```python
class Authentication:

    @staticmethod
    def log_in(username, password):
        # Log in to get a JWT token (expires in 12 hours)
        response = requests.post(
            "https://api.computex.ai/api/v1/users/login",
            headers={"accept": "application/json",
                     "Content-Type": "application/json"
                     },
            json={"email": username, "password": password},
        )
        if response.status_code != 200:
            raise Exception("Log in failed.")
        token = response.json()["token"]
        return token

    @staticmethod
    def generate_headers(token):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        return headers
```

## Set the build configuration
The build configuration can be adjusted to match the exact specs required.

The example below creates a 8 node GPU build using the NVIDIA RTX A600 for training. Set the `name`, `username`, and `password` to the desired values for your project.

```python
authentication = Authentication()
token = authentication.log_in(COMPUTEX_USERNAME, COMPUTEX_PASSWORD)
headers = authentication.generate_headers(token)

spec = {
    "name": "virtual-server-name",
    "num_cpu_cores": 96,
    "num_gpu": 8,
    "gpu_sku": "RTX_A6000",
    "memory": 696,
    "storage_size_in_GiB": 300,
    "username": "username",
    "password": "password",
}

response = requests.post(
    f"{URL}/virtual-servers",
    headers=headers,
    json=spec,
)

if 200 <= response.status_code < 300:
    print(response.json())
else:
    print(f"error: {response.status_code}, message: {response.text}")
```

### Available GPUs:
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

## Get the external IP address
Get the external IP address to SSH into the virtual server using the name

```python
virtual_server_name = "virtual-server-name"
response = requests.get(
    f"https://api.computex.ai/api/v1/virtual-servers/{virtual_server_name}/status",
    headers=headers,
)

if 200 <= response.status_code < 300:
    response_server_status = response.json()
    external_ip = response_server_status["status"]["network"]["externalIP"]
    print("external ip  ", external_ip)
else:
    print(f"error: {response.status_code}, message: {response.text}")
```

After extracting the external ip address, SSH into the server using the username

`ssh <username>@<external-ip>`
i.e. `ssh john@74.64.162.111`
