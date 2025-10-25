"""
RunPod Serverless Handler for Video2X Video Upscaling
Handles video download, upscaling with Video2X, and returns base64-encoded result
"""

import runpod
import subprocess
import os
import requests
import json
import base64
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
        
        print(f"Downloaded successfully to: {output_path}")
        return True
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

def upscale_video(input_path: str, output_path: str, scale: int = 4) -> bool:
    """Upscale video using Video2X"""
    try:
        print(f"Starting Video2X upscaling (scale: {scale}x)...")
        
        # Video2X command for upscaling with Real-ESRGAN
        cmd = [
            "/usr/local/bin/video2x",
            "-i", input_path,
            "-o", output_path,
            "-p3", "upscale",
            "-a", "realesr-animevideov3",
            "-s", str(scale)
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"Video2X error (stderr): {result.stderr}")
            print(f"Video2X error (stdout): {result.stdout}")
            return False
        
        print("Video2X upscaling completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("Video2X process timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error during upscaling: {str(e)}")
        return False

def handler(job):
    """Main RunPod handler function"""
    try:
        job_input = job['input']
        video_url = job_input.get('video_url')
        scale = job_input.get('scale', 4)
        
        if not video_url:
            return {"error": "video_url is required"}
        
        # Create temp directory
        work_dir = Path("/workspace/temp")
        work_dir.mkdir(exist_ok=True)
        
        # Define file paths
        input_video = work_dir / "input.mp4"
        output_video = work_dir / "output.mp4"
        
        # Download video
        if not download_video(video_url, str(input_video)):
            return {"error": "Failed to download video"}
        
        # Upscale video
        if not upscale_video(str(input_video), str(output_video), scale):
            return {"error": "Failed to upscale video"}
        
        # Read upscaled video and encode to base64
        print("Encoding video to base64...")
        with open(output_video, 'rb') as f:
            video_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Cleanup
        input_video.unlink(missing_ok=True)
        output_video.unlink(missing_ok=True)
        
        print("Job completed successfully!")
        
        return {
            "video_data": video_data,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
