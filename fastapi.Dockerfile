# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone REDACTED@github.com/flowtra/The-Black-Hole-Group-Dashboard.git .

RUN pip3 install -r requirements.txt
RUN pip3 install fastapi uvicorn


EXPOSE 8000

ENTRYPOINT ["uvicorn", "apiController:app", "--host", "0.0.0.0", "--port", "8000"]