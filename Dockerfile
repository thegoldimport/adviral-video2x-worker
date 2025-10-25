FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install RunPod SDK
RUN pip install --no-cache-dir runpod requests

# Download Video2X AppImage
RUN wget https://github.com/k4yt3x/video2x/releases/download/6.4.0/Video2X-x86_64.AppImage -O /usr/local/bin/video2x && \
    chmod +x /usr/local/bin/video2x

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python", "-u", "/handler.py"]
