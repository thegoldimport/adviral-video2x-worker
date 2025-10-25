FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install RunPod SDK
RUN pip3 install --no-cache-dir runpod requests

# Download and install Video2X binary
RUN wget https://github.com/k4yt3x/video2x/releases/download/6.4.0/video2x-linux-amd64 -O /usr/local/bin/video2x && \
    chmod +x /usr/local/bin/video2x

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python3", "-u", "/handler.py"]
