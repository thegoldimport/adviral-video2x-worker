FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Video2X from pip (official package)
RUN pip install --no-cache-dir video2x

# Install RunPod SDK
RUN pip install --no-cache-dir runpod requests

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python", "-u", "/handler.py"]
