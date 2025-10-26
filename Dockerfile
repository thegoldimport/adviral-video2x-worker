FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system essentials
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    wget \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install NumPy 1.26.4 FIRST (before anything else)
RUN pip install numpy==1.26.4

# Install PyTorch with CUDA support (compatible with NumPy 1.26.4)
RUN pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Install Real-ESRGAN and dependencies
RUN pip install \
    opencv-python-headless \
    realesrgan \
    basicsr \
    facexlib \
    gfpgan \
    runpod \
    requests

# Download model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python3", "-u", "/handler.py"]
