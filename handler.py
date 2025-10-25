"""
RunPod Serverless Handler for Video2X Video Upscaling
Handles video download, upscaling with Video2X, and returns result
"""
import runpod
import subprocess
import os
import requests
import json
from pathlib import Path

def download_video(url: str, output_path: str) -> bool:
    """Download video from URL to local path"""
    try:
        print(f"Downloading video from: {url}")
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(output_path)
        print(f"Downloaded video: {file_size} bytes")
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

def upscale_video(input_path: str, output_path: str, scale: int = 4) -> bool:
    """Upscale video using Video2X with Real-ESRGAN"""
    try:
        print(f"Starting upscale: {input_path} -> {output_path} (scale={scale}x)")
        
        # Video2X command with Real-ESRGAN
        cmd = [
            "video2x",
            "-i", input_path,
            "-o", output_path,
            "-p", "realesrgan",
            "-r", str(scale),
            "-v", "realesr-animevideov3"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"Video2X error: {result.stderr}")
            return False
        
        if not os.path.exists(output_path):
            print("Output file not created")
            return False
        
        output_size = os.path.getsize(output_path)
        print(f"Upscaled video created: {output_size} bytes")
        return True
        
    except subprocess.TimeoutExpired:
        print("Upscaling timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error upscaling video: {e}")
        return False

def handler(event):
    """RunPod serverless handler"""
    try:
        input_data = event.get("input", {})
        video_url = input_data.get("video_url")
        scale = input_data.get("scale", 4)
        
        if not video_url:
            return {"error": "Missing video_url parameter"}
        
        workspace = Path("/workspace")
        workspace.mkdir(exist_ok=True)
        
        input_path = workspace / "input.mp4"
        output_path = workspace / "output.mp4"
        
        for path in [input_path, output_path]:
            if path.exists():
                path.unlink()
        
        if not download_video(video_url, str(input_path)):
            return {"error": "Failed to download video"}
        
        if not upscale_video(str(input_path), str(output_path), scale):
            return {"error": "Failed to upscale video"}
        
        import base64
        with open(output_path, "rb") as f:
            video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        
        input_path.unlink()
        output_path.unlink()
        
        return {
            "video_data": video_base64,
            "status": "success",
            "upscaled_size": len(video_bytes)
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
