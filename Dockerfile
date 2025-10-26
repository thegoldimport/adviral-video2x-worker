# Use RunPod's lightweight serverless GPU base (<10GB total)
FROM runpod/serverless-gpu:cu118-py3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with compatible versions
RUN pip install --no-cache-dir \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3 \
    Pillow==10.0.1 \
    realesrgan==0.3.0 \
    requests

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
