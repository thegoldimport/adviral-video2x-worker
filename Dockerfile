FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python and essentials
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch 2.0.1 with CUDA 11.8 (proven compatible)
RUN pip3 install torch==2.0.1 torchvision==0.15.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install NumPy 1.24.3 (proven compatible with Real-ESRGAN)
RUN pip3 install numpy==1.24.3 opencv-python pillow

# Install Real-ESRGAN dependencies
RUN pip3 install basicsr facexlib gfpgan realesrgan runpod requests

# Download model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python3", "-u", "/handler.py"]
