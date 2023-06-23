# Getting Started

Guide to deploying models using the CX CLI.

## Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up an Account on CX](#set-up-an-account-on-cx)
3. [Installation](#installation)
4. [Creating an Image with Cog](#creating-an-image-with-cog)
    - [Initialize Project](#initialize-project)
    - [Customize `cog.yaml` file](#customize-cog-yaml-file)
    - [Implement Predict Functionality](#implement-predict-functionality)
    - [Supported Input and Output Types](#supported-input-and-output-types)
    - [Build an Image](#build-an-image)
5. [Testing Locally](#testing-your-image-locally)
6. [Next steps](#next-steps)



## Prerequisites

* **MacOS** or **Linux** Operating system
* **Docker**. CX CLI uses Docker to package images. Get it from [here](https://docs.docker.com/get-docker/).
* **pip**. for installing the CX CLI
* **python 3.8**. Or higher
* **Cog** (optional). An Open Source package to simplify the process of creating a container. 


## Set up an account on CX
Sign up for an account on [computex.dev](https://www.computex.dev/). You will receive a confirmation email with your access key.

## Installation

Install the CX CLI using pip:

```bash
$ pip install computex-cli
```

Optionally, install Cog to simplify container deployment:

```bash
$ sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
$ sudo chmod +x /usr/local/bin/cog
```

## Creating an image with Cog

The instructions below are the spark notes to creating an image with Cog. Check out their open-source [project](https://github.com/replicate/cog) for full documentation.

You will only need to utilize this package to build the image.

### Initialize project
Create a directory for the project and initialize it with Cog.

```bash
$ mkdir my_project
$ cd my_project
$ cog init
```

This creates a base project with `predict.py` and `cog.yaml` files.

### Customize Cog YAML file 

Customize `cog.yaml` to include the python and system libraries required by your project. It could look something like this:

```yaml
build:
  # set to true if your model requires a GPU
  gpu: true

  system_packages:
    - "ffmpeg"

  python_version: "3.8"

  # a list of packages in the format <package-name>==<version>
  python_packages:
    - "openai-whisper>=20230314"
    - "setuptools-rust"

  run:
    - echo "Run system commands here, if necessary"

# predict.py defines how predictions are run on your model
predict: "predict.py:Predictor"
```
### Implement Predict Functionality
Implement the logic to call your model in predict.py. Below is a simple implementation of OpenAI's Whisper:

```python
from cog import BasePredictor, Input
import requests
import tempfile
import whisper


class Predictor(BasePredictor):
    def setup(self):
        self.model = whisper.load_model("tiny")

    def predict(
        self,
        audio_url: str = Input(description="URL to audio file"),
    ) -> str:
        """Run a single prediction on the model"""
        response = requests.get(audio_url)
        audio_data = response.content
        file_type = audio_url.split('.')[-1]

        with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False) as audio_file:
            audio_file.write(audio_data)
            result = self.model.transcribe(audio_file.name)

        return result["text"]
```

#### Supported input and output types:
- `str`: a string
- `int`: an integer
- `float`: a floating point number
- `bool`: a boolean
- Note: if you need to pass a file, pass it as a URL. Example here.

### Build an image

After you've set up everything, you can build your image. Remember, always use a new tag for your image. This ensures the most recent version of the image is used, as our system caches aggressively for speedy startup times.

```bash
$ cog build -t <image>:<tag>
```

Note: Always push images under a new tag. Our system uses aggressive caching to speed up startup times. Reusing an old tag could result in running an outdated version of the image.

## Testing Your image Locally
Run the command below and navigate to the provided URL to check if everything works as expected before deploying your model.


```bash
# On CPU
$ docker run -p 5000:5000 <image>:<tag>

# On GPU
$ docker run --gpus all -p 5000:5000 <image>:<tag>
```

Now, open your browser and go to: http://localhost:5000/docs#
Modify the Request body for the `/predictions` endpoint to test your model. 

For the OpenAI whisper example, it could look something like this:

```yaml
{
  "input": {
    "audio_url": "https://pub-96e94511d3fe43ae820c4c5ecc11c66e.r2.dev/03db38d7ad724f749711ecfc81356441-2023_06_14_05_10_06_234-short_clip.mp3"
  }
}
```

# Next Steps
* [A guide to deploying a model](docs/deploying.md)
* [A guide to running predictions on a model](docs/predictions.md)