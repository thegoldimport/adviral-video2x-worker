FROM k4yt3x/video2x:6.0.0

RUN pip install --no-cache-dir runpod requests

RUN mkdir -p /workspace

COPY handler.py /handler.py

WORKDIR /workspace

CMD ["python", "-u", "/handler.py"]
