from python:3.10

workdir /root

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpcre3-dev protobuf-compiler libprotobuf-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

copy requirements.txt .

run pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends lsof jq htop && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
