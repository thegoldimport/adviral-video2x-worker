"""
RunPod Serverless Handler for Real-ESRGAN Video Upscaling
"""

import runpod
import os
import requests
import base64
import subprocess
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
        
        print(f"Downloaded successfully")
        return True
    except Exception as e:
        print(f"Error downloading: {str(e)}")
        return False

def extract_frames(video_path: str, frames_dir: str) -> bool:
    """Extract frames from video using FFmpeg"""
    try:
        Path(frames_dir).mkdir(exist_ok=True)
        cmd = [
            "ffmpeg", "-i", video_path,
            "-qscale:v", "1", "-qmin", "1", "-qmax", "1",
            f"{frames_dir}/frame%08d.png"
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"Frame extraction error: {e}")
        return False

def upscale_frames(input_dir: str, output_dir: str) -> bool:
    """Upscale frames using Real-ESRGAN"""
    try:
        Path(output_dir).mkdir(exist_ok=True)
        cmd = [
            "python", "-m", "realesrgan.inference_realesrgan",
            "-i", input_dir,
            "-o", output_dir,
            "-n", "realesr-animevideov3",
            "-s", "4",
            "--model_path", "/workspace/models/realesr-animevideov3.pth",
            "--fp32"
        ]
        print(f"Running Real-ESRGAN...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        if result.returncode != 0:
            print(f"Real-ESRGAN error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Upscaling error: {e}")
        return False

def rebuild_video(frames_dir: str, output_path: str, original_video: str) -> bool:
    """Rebuild video from upscaled frames"""
    try:
        # Get original framerate
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            original_video
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        fps = eval(result.stdout.strip())  # e.g., "30/1" -> 30.0
        
        # Rebuild video
        cmd = [
            "ffmpeg", "-framerate", str(fps),
            "-i", f"{frames_dir}/frame%08d_out.png",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"Video rebuild error: {e}")
        return False

def handler(job):
    """Main RunPod handler"""
    try:
        video_url = job['input'].get('video_url')
        if not video_url:
            return {"error": "video_url required"}
        
        work_dir = Path("/workspace/temp")
        work_dir.mkdir(exist_ok=True)
        
        input_video = work_dir / "input.mp4"
        frames_dir = work_dir / "frames"
        upscaled_dir = work_dir / "upscaled"
        output_video = work_dir / "output.mp4"
        
        # Download
        if not download_video(video_url, str(input_video)):
            return {"error": "Download failed"}
        
        # Extract frames
        print("Extracting frames...")
        if not extract_frames(str(input_video), str(frames_dir)):
            return {"error": "Frame extraction failed"}
        
        # Upscale
        print("Upscaling frames...")
        if not upscale_frames(str(frames_dir), str(upscaled_dir)):
            return {"error": "Upscaling failed"}
        
        # Rebuild
        print("Rebuilding video...")
        if not rebuild_video(str(upscaled_dir), str(output_video), str(input_video)):
            return {"error": "Video rebuild failed"}
        
        # Encode to base64
        print("Encoding result...")
        with open(output_video, 'rb') as f:
            video_data = base64.b64encode(f.read()).decode('utf-8')
        
        print("Success!")
        return {"video_data": video_data, "status": "success"}
        
    except Exception as e:
        print(f"Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
