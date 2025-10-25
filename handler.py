"""
RunPod Serverless Handler for Real-ESRGAN Video Upscaling
"""

import runpod
import os
import requests
import base64
import subprocess
import cv2
import torch
from pathlib import Path
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

def download_video(url: str, output_path: str) -> bool:
    """Download video from URL"""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete")
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def upscale_video(input_path: str, output_path: str, scale: int = 4) -> bool:
    """Upscale video using Real-ESRGAN"""
    try:
        print("Initializing Real-ESRGAN...")
        
        # Load model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        upsampler = RealESRGANer(
            scale=4,
            model_path='/workspace/models/realesr-animevideov3.pth',
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True,
            device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        )
        
        print("Processing video...")
        
        # Open input video
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create temporary directory for frames
        temp_dir = Path(input_path).parent / "temp_frames"
        temp_dir.mkdir(exist_ok=True)
        
        frame_count = 0
        upscaled_frames = []
        
        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Upscale frame
            output, _ = upsampler.enhance(frame, outscale=4)
            upscaled_frames.append(output)
            
            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Processed {frame_count} frames...")
        
        cap.release()
        print(f"Total frames processed: {frame_count}")
        
        # Write upscaled video
        if not upscaled_frames:
            print("No frames to write")
            return False
        
        out_height, out_width = upscaled_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))
        
        for frame in upscaled_frames:
            out.write(frame)
        
        out.release()
        print("Video written successfully")
        return True
        
    except Exception as e:
        print(f"Upscaling error: {e}")
        import traceback
        traceback.print_exc()
        return False

def handler(job):
    """Main handler"""
    try:
        video_url = job['input'].get('video_url')
        if not video_url:
            return {"error": "video_url required"}
        
        work_dir = Path("/workspace/temp")
        work_dir.mkdir(exist_ok=True)
        
        input_video = work_dir / "input.mp4"
        output_video = work_dir / "output.mp4"
        
        # Download
        if not download_video(video_url, str(input_video)):
            return {"error": "Download failed"}
        
        # Upscale
        print("Starting upscale...")
        if not upscale_video(str(input_video), str(output_video)):
            return {"error": "Upscale failed"}
        
        # Check output exists
        if not output_video.exists():
            return {"error": "Output video not created"}
        
        # Encode to base64
        print("Encoding to base64...")
        with open(output_video, 'rb') as f:
            video_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Cleanup
        input_video.unlink(missing_ok=True)
        output_video.unlink(missing_ok=True)
        
        print("Complete!")
        return {"video_data": video_data, "status": "success"}
        
    except Exception as e:
        print(f"Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
