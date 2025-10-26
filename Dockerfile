FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install compatible PyTorch + torchvision
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies with compatible versions
RUN pip install --no-cache-dir \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3 \
    Pillow==10.0.1 \
    tqdm \
    requests \
    runpod==1.6.2

# Install Real-ESRGAN (this will install compatible basicsr)
RUN pip install --no-cache-dir realesrgan==0.3.0

# Create workspace
WORKDIR /workspace
RUN mkdir -p /workspace/models

# Download model
RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /workspace/handler.py

CMD ["python", "-u", "/workspace/handler.py"]
