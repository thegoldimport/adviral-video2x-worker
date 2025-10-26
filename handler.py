"""
RunPod Serverless Handler for Real-ESRGAN Video Upscaling
Uses Real-ESRGAN Python API directly (no Video2X, no FUSE required)
"""
import runpod
import subprocess
import os
import requests
import base64
import cv2
import numpy as np
from pathlib import Path
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

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
        print(f"Downloaded successfully: {file_size} bytes")
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def extract_frames(video_path: str, frames_dir: str) -> tuple:
    """Extract frames from video using ffmpeg"""
    try:
        print("Extracting frames...")
        Path(frames_dir).mkdir(parents=True, exist_ok=True)
        
        # Extract frames as PNG
        cmd = [
            "ffmpeg", "-i", video_path,
            "-qscale:v", "1",
            f"{frames_dir}/frame_%04d.png"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"FFmpeg extract error: {result.stderr}")
            return 0, 0.0
        
        # Get frame count and FPS
        frames = list(Path(frames_dir).glob("frame_*.png"))
        frame_count = len(frames)
        
        # Get FPS
        fps_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        fps_result = subprocess.run(fps_cmd, capture_output=True, text=True)
        fps_str = fps_result.stdout.strip()
        
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den)
        else:
            fps = 30.0
        
        print(f"Extracted {frame_count} frames at {fps:.2f} FPS")
        return frame_count, fps
        
    except Exception as e:
        print(f"Frame extraction error: {e}")
        return 0, 0.0

def upscale_frames(frames_dir: str, output_dir: str, scale: int = 4) -> bool:
    """Upscale frames using Real-ESRGAN GPU processing"""
    try:
        print(f"Upscaling frames (scale: {scale}x)...")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Real-ESRGAN model
        model_path = "/workspace/models/realesr-animevideov3.pth"
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True,
            gpu_id=0
        )
        
        # Process each frame
        frames = sorted(Path(frames_dir).glob("frame_*.png"))
        total = len(frames)
        
        for idx, frame_path in enumerate(frames, 1):
            img = cv2.imread(str(frame_path), cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Failed to read: {frame_path}")
                continue
            
            output, _ = upsampler.enhance(img, outscale=scale)
            
            output_path = Path(output_dir) / frame_path.name
            cv2.imwrite(str(output_path), output)
            
            if idx % 10 == 0 or idx == total:
                print(f"Progress: {idx}/{total} frames ({idx*100//total}%)")
        
        print(f"Upscaled {total} frames successfully")
        return True
        
    except Exception as e:
        print(f"Upscaling error: {e}")
        import traceback
        traceback.print_exc()
        return False

def rebuild_video(frames_dir: str, output_path: str, original_video: str, fps: float) -> bool:
    """Rebuild video from upscaled frames and preserve audio"""
    try:
        print("Rebuilding video...")
        
        temp_video = "/workspace/temp/video_no_audio.mp4"
        Path(temp_video).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", f"{frames_dir}/frame_%04d.png",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            temp_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"FFmpeg rebuild error: {result.stderr}")
            return False
        
        # Merge audio from original video
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-i", original_video,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-shortest",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"FFmpeg audio merge error: {result.stderr}")
            import shutil
            shutil.copy(temp_video, output_path)
        
        file_size = os.path.getsize(output_path)
        print(f"Video rebuilt successfully: {file_size} bytes")
        return True
        
    except Exception as e:
        print(f"Rebuild error: {e}")
        return False

def handler(event):
    """RunPod serverless handler for Real-ESRGAN video upscaling"""
    try:
        input_data = event.get("input", {})
        video_url = input_data.get("video_url")
        scale = input_data.get("scale", 4)
        
        if not video_url:
            return {"error": "Missing video_url parameter"}
        
        print(f"Starting Real-ESRGAN upscaling (scale: {scale}x)")
        
        workspace = Path("/workspace/temp")
        workspace.mkdir(parents=True, exist_ok=True)
        
        input_video = workspace / "input.mp4"
        output_video = workspace / "output.mp4"
        frames_dir = workspace / "frames"
        upscaled_dir = workspace / "upscaled"
        
        # Clean up previous run
        for path in [input_video, output_video]:
            if path.exists():
                path.unlink()
        for dir_path in [frames_dir, upscaled_dir]:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
        
        # Download video
        if not download_video(video_url, str(input_video)):
            return {"error": "Failed to download video"}
        
        # Extract frames
        frame_count, fps = extract_frames(str(input_video), str(frames_dir))
        if frame_count == 0:
            return {"error": "Failed to extract frames"}
        
        # Upscale frames
        if not upscale_frames(str(frames_dir), str(upscaled_dir), scale):
            return {"error": "Failed to upscale frames"}
        
        # Rebuild video
        if not rebuild_video(str(upscaled_dir), str(output_video), str(input_video), fps):
            return {"error": "Failed to rebuild video"}
        
        # Encode as base64
        with open(output_video, "rb") as f:
            video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        
        # Cleanup
        import shutil
        shutil.rmtree(workspace)
        
        print("Upscaling completed successfully!")
        
        return {
            "video_data": video_base64,
            "status": "success",
            "frames_processed": frame_count,
            "output_size": len(video_bytes)
        }
        
    except Exception as e:
        print(f"Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
