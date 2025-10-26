FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set Python as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch with CUDA support (compatible versions)
RUN pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# Install Real-ESRGAN and dependencies (exact versions that work)
RUN pip install --no-cache-dir \
    opencv-python==4.8.1.78 \
    numpy==1.24.3 \
    Pillow==10.0.1 \
    tqdm \
    requests

# Install basicsr and Real-ESRGAN from source (fresher, more compatible)
RUN pip install git+https://github.com/xinntao/BasicSR.git
RUN pip install git+https://github.com/xinntao/Real-ESRGAN.git

# Install RunPod SDK
RUN pip install runpod==1.6.2

# Create workspace
WORKDIR /workspace
RUN mkdir -p /workspace/models

# Download Real-ESRGAN model (same one Video2X uses)
RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /workspace/handler.py

CMD ["python", "-u", "/workspace/handler.py"]
