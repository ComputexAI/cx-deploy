FROM python:3.10-slim

WORKDIR /downloader

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY model_download.py ./

ENTRYPOINT ["python3", "model_download.py"]