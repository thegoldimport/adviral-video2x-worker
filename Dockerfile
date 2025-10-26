# Use NVIDIA's official CUDA runtime (lightweight GPU image)
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.10 and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install compatible PyTorch + torchvision FIRST
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
RUN pip install --no-cache-dir \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3 \
    Pillow==10.0.1 \
    requests \
    runpod==1.6.2

# Install Real-ESRGAN (will use already-installed PyTorch)
RUN pip install --no-cache-dir realesrgan==0.3.0

# Create workspace and models directory
RUN mkdir -p /workspace/models

# Download Real-ESRGAN model
RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /workspace/handler.py

WORKDIR /workspace

# RunPod serverless handler
CMD ["python", "-u", "/workspace/handler.py"]
