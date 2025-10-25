FROM ghcr.io/k4yt3x/video2x:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir runpod requests

COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python3", "-u", "/handler.py"]
