FROM ghcr.io/k4yt3x/video2x:latest

# Install Python for RunPod handler
RUN apk add --no-cache python3 py3-pip

# Install RunPod SDK
RUN pip3 install --no-cache-dir --break-system-packages runpod requests

# Copy handler
COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python3", "-u", "/handler.py"]
