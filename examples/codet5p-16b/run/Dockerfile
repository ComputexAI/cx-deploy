FROM ghcr.io/coreweave/ml-containers/torch:bb02bee-base-cuda11.8.0-torch2.0.0-vision0.15.1-audio2.0.1

RUN mkdir -p /transformer/
WORKDIR /transformer

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY predict.py .
COPY load_model.py .

ENTRYPOINT ["uvicorn", "predict:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "18000", "--lifespan", "on"]
