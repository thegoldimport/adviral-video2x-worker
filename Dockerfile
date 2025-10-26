FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system essentials
RUN apt-get update && apt-get install -y \
    wget \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:$PATH"

# Create isolated environment with exact versions
RUN conda create -n realesrgan python=3.10 -y && \
    /opt/conda/envs/realesrgan/bin/pip install --no-cache-dir \
    numpy==1.26.4 \
    torch==2.1.0 \
    torchvision==0.16.0 \
    opencv-python-headless==4.8.1.78 \
    realesrgan==0.3.0 \
    basicsr==1.4.2 \
    facexlib==0.3.0 \
    gfpgan==1.3.8 \
    runpod==1.7.3 \
    requests==2.31.0

# Download model
RUN mkdir -p /workspace/models && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth \
    -O /workspace/models/realesr-animevideov3.pth

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

# Run handler in isolated conda env
CMD ["/opt/conda/envs/realesrgan/bin/python", "-u", "/handler.py"]
