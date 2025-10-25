FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Real-ESRGAN
RUN pip install --no-cache-dir realesrgan basicsr facexlib gfpgan

# Install RunPod SDK
RUN pip install --no-cache-dir runpod requests opencv-python-headless

# Download Real-ESRGAN model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python", "-u", "/handler.py"]
