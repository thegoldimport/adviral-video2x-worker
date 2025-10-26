FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install compatible PyTorch and torchvision versions
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install Real-ESRGAN with compatible dependencies
RUN pip install --no-cache-dir \
    basicsr==1.4.2 \
    facexlib==0.3.0 \
    gfpgan==1.3.8 \
    realesrgan==0.3.0 \
    opencv-python==4.8.1.78 \
    numpy==1.24.3 \
    runpod==1.6.2

# Create workspace directory
WORKDIR /workspace

# Download Real-ESRGAN model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /workspace/handler.py

# Set entry point
CMD ["python", "-u", "/workspace/handler.py"]
