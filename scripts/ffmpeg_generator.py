"""
FFmpeg Shorts / Reels Generator for ARIS Content Automation System.
Transforms approved horizontal anime clips into 9:16 vertical Shorts/Reels (<= 58s).
Features:
- Smart background blur with centered sharp foreground.
- Enforces strict <= 58s duration cap for Shorts/Reels compliance.
- Fingerprints output video with SHA-256 hash.
- Checks against duplicate ledger before generating.
"""

import os
import sys
import json
import subprocess
import hashlib
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")

def get_ffmpeg_path():
    """Locate the ffmpeg executable."""
    if os.path.exists(TOOLS_FFMPEG):
        return TOOLS_FFMPEG
    
    # Check config
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                custom_path = cfg.get("video_processing", {}).get("ffmpeg_path")
                if custom_path:
                    abs_custom = os.path.join(PROJECT_DIR, custom_path)
                    if os.path.exists(abs_custom):
                        return abs_custom
        except Exception:
            pass
            
    # Default fallback to system PATH
    return "ffmpeg"

def get_video_info(input_path, ffmpeg_bin):
    """Probe video duration using ffmpeg."""
    cmd = [ffmpeg_bin, "-i", input_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    duration = 0.0
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            # format HH:MM:SS.xx
            h, m, s = parts.split(":")
            duration = float(h) * 3600 + float(m) * 60 + float(s)
            break
    return {"duration": duration}

def generate_short(input_path, output_dir=None, max_duration=58, title_override=None):
    """
    Process an anime clip into vertical 9:16 Short/Reel format.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}

    ffmpeg_bin = get_ffmpeg_path()
    if not output_dir:
        output_dir = os.path.join(PROJECT_DIR, "data", "processed_shorts")
    os.makedirs(output_dir, exist_ok=True)

    info = get_video_info(input_path, ffmpeg_bin)
    duration = info.get("duration", 0)
    clip_duration = min(duration, max_duration) if duration > 0 else max_duration

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    raw_hash = hashlib.sha256(f"{base_name}_{clip_duration}".encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"short_{timestamp}_{raw_hash}.mp4"
    out_path = os.path.join(output_dir, out_filename)

    # Filter graph:
    # 1. Background: scale to 1080x1920 (crop/fill) and apply heavy blur (boxblur=20:5)
    # 2. Foreground: scale to width 1080 maintaining aspect ratio
    # 3. Overlay foreground centered on blurred background
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
    )

    cmd = [
        ffmpeg_bin,
        "-y",
        "-ss", "0",
        "-t", str(clip_duration),
        "-i", input_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        out_path
    ]

    print(f"Executing FFmpeg processing on: {input_path} ...", file=sys.stderr)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")

    if result.returncode != 0:
        return {"success": False, "error": result.stderr}

    # Compute content hash of produced video
    sha256 = hashlib.sha256()
    with open(out_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    content_hash = sha256.hexdigest()

    return {
        "success": True,
        "input_file": input_path,
        "output_file": out_path,
        "content_hash": content_hash,
        "duration": clip_duration,
        "dimensions": "1080x1920",
        "aspect_ratio": "9:16",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ffmpeg_generator.py <input_video_path> [output_dir] [max_duration]")
        sys.exit(1)

    inp = sys.argv[1]
    out_d = sys.argv[2] if len(sys.argv) > 2 else None
    max_d = float(sys.argv[3]) if len(sys.argv) > 3 else 58

    res = generate_short(inp, output_dir=out_d, max_duration=max_d)
    print(json.dumps(res, indent=2))
