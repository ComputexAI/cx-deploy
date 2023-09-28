FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip

# Set up work directory
WORKDIR /downloader

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model_download.py ./

ENTRYPOINT ["python3", "model_download.py"]
