# Getting Started

Build, deploy, and run predictions on models at a fraction of the cost through the CX platform. 

Each deployment is highly configurable to run optimally.

## Prerequisites

* **MacOS** or **Linux** Operating system
* **Docker**. the CX CLI uses Docker to package images. Get it from [here](https://docs.docker.com/get-docker/).
* **pip**. for installing the CX CLI
* **python 3.8**. Or higher

## Set up an account
Sign up for an account on [computex.dev](https://www.computex.dev/). You will receive a confirmation email with your access key.

## Installation

Install the CX CLI using pip:

```bash
$ pip install computex-cli
```

## Deploying with CX

Leverage an extensive range of fully configurable GPU & CPU machine configurations to match any deployment. 


| GPU Model          | VRAM (GB) | Max vCPUs | Max RAM (GB) |
|--------------------|-----------|-----------|--------------|
| NVIDIA H100 PCIe   | 80        | 48        | 256          |
| A100 80GB NVLINK   | 80        | 48        | 256          |
| A100 80GB PCIe     | 80        | 48        | 256          |
| A100 40GB NVLINK   | 40        | 48        | 256          |
| A100 40GB PCIe     | 40        | 48        | 256          |
| A40                | 48        | 48        | 256          |
| RTX A6000          | 48        | 48        | 256          |
| RTX A5000          | 24        | 36        | 128          |
| RTX A4000          | 16        | 36        | 128          |
| Quadro RTX 5000    | 16        | 36        | 128          |
| Quadro RTX 4000    | 8         | 36        | 128          |
| Tesla V100 NVLINK  | 16        | 36        | 128          |


# Next Steps
* [Building an image](docs/building-an-image.md)
* [Deploying a model](docs/deploying.md)
* [Running predictions on a model](docs/predictions.md)