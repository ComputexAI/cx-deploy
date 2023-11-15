# First stage: Build
FROM python:3.9-slim as builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Execution
FROM python:3.9-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg

COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

COPY predict.py .

ENTRYPOINT ["uvicorn", "predict:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "18000", "--lifespan", "on"]
