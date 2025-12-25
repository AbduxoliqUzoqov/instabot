FROM python:3.11-slim

RUN apt update && apt install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 1 \
  -b 0.0.0.0:8080
