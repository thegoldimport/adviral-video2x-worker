FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# CRITICAL: Force reinstall NumPy 1.x and all dependencies
RUN pip uninstall -y numpy && \
    pip install --force-reinstall --no-cache-dir "numpy==1.26.4"

# Reinstall Real-ESRGAN with NumPy 1.x
RUN pip install --force-reinstall --no-cache-dir \
    realesrgan \
    basicsr \
    facexlib \
    gfpgan \
    opencv-python-headless

# Install RunPod SDK
RUN pip install --no-cache-dir runpod requests

# Download Real-ESRGAN model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python", "-u", "/handler.py"]
