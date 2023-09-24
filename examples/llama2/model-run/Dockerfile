FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip

WORKDIR /transformer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY predict.py .
COPY load_model.py .

ENTRYPOINT ["uvicorn", "predict:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "18000", "--lifespan", "on"]
