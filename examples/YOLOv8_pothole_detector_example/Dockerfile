# Stage 1: Build the application
FROM python:3.10.3-slim as builder

WORKDIR /build

COPY app.py .
COPY inference.py .
COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Stage 2: Create the final runtime image
FROM python:3.10.3-slim

WORKDIR /app

COPY --from=builder /build/app.py .
COPY --from=builder /build/inference.py .
COPY --from=builder /build/requirements.txt .

RUN apt-get update 

###################################################
# Install any system dependencies your app needs here
RUN apt-get install -y libgl1-mesa-glx libglib2.0-0  \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
###################################################

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Run the application with port 8000 exposed
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

