"""
FFmpeg Shorts / Reels Generator for ARIS Content Automation System.
Transforms anime clips into stunning 9:16 vertical Shorts/Reels (<= 58s).

Key Features:
- Multi-Style Adaptive Video Engine:
    1. Fullscreen Action 9:16 (Center Crop full bleed - viral TikTok/Shorts style)
    2. Obsidian Cinematic Letterbox (Sleek dark matte theater framing)
    3. Dark Ambient Spotlight (Deep mood lighting backdrop with spotlight vignette)
    4. Native Vertical Remaster (For clips already in 9:16 format)
- Razor-sharp 4K visual remastering (unsharp mask, rich contrast, dynamic saturation)
- Movie-theater audio enhancement (punchy bass EQ for impacts, crisp treble for sound effects)
- Strict <= 58s duration cap for Shorts/Reels compliance
- Fingerprints output video with SHA-256 hash
"""

import os
import sys
import json
import random
import re
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
            
    import shutil
    return shutil.which("ffmpeg") or "ffmpeg"

def get_video_info(input_path, ffmpeg_bin):
    """Probe video duration, dimensions, and audio presence using ffmpeg."""
    cmd = [ffmpeg_bin, "-i", input_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    duration = 0.0
    has_audio = False
    width = 1920
    height = 1080
    for line in proc.stderr.splitlines():
        if "Duration:" in line and duration == 0.0:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            duration = float(h) * 3600 + float(m) * 60 + float(s)
        if "Audio:" in line:
            has_audio = True
        if "Video:" in line:
            m = re.search(r"(\d{3,4})x(\d{3,4})", line)
            if m:
                width = int(m.group(1))
                height = int(m.group(2))
    return {"duration": duration, "has_audio": has_audio, "width": width, "height": height}

def build_adaptive_filter(width, height, clip_duration, style_index=None):
    """
    Constructs high-aesthetic, diverse FFmpeg filter graphs based on aspect ratio and style.
    Guarantees every video has a distinct visual personality!
    """
    is_already_vertical = height > int(width * 1.2)

    if is_already_vertical:
        # Native vertical format - full bleed 4K remaster
        style_name = "NATIVE_VERTICAL_4K"
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=contrast=1.12:saturation=1.20:brightness=0.01,"
            "unsharp=5:5:0.8:5:5:0.0,vignette=PI/4.5,setpts=PTS/1.04[v]"
        )
        return filter_complex, style_name

    # For horizontal / 16:9 widescreen video, offer 3 diverse editing styles:
    styles = [
        (
            "ACTION_FULLSCREEN_916",
            (
                "[0:v]crop=in_h*9/16:in_h:(in_w-out_w)/2:0,scale=1080:1920,"
                "eq=contrast=1.15:saturation=1.24:brightness=0.01,"
                "unsharp=5:5:1.0:5:5:0.0,vignette=PI/4.4,setpts=PTS/1.04[v]"
            )
        ),
        (
            "CINEMATIC_OBSIDIAN_THEATER",
            (
                f"color=c=0x0a0c14:s=1080x1920:d={clip_duration:.2f}[bg];"
                "[0:v]scale=1080:-2,eq=contrast=1.12:saturation=1.20:brightness=0.01,unsharp=5:5:0.9[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,setpts=PTS/1.04[v]"
            )
        ),
        (
            "DARK_AMBIENT_SPOTLIGHT",
            (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "boxblur=42:6,eq=brightness=-0.42:contrast=1.35:saturation=1.45[bg];"
                "[0:v]crop=in_w*0.96:in_h*0.96,scale=1080:-2,eq=contrast=1.10:saturation=1.18,unsharp=5:5:0.8[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,vignette=PI/4.2,setpts=PTS/1.04[v]"
            )
        )
    ]

    if style_index is None:
        style_index = random.randint(0, len(styles) - 1)
    else:
        style_index = style_index % len(styles)

    chosen_style, filter_str = styles[style_index]
    return filter_str, chosen_style

def generate_short(input_path, output_dir=None, max_duration=58, style_index=None):
    """
    Process an anime clip into vertical 9:16 Short/Reel format with high-aesthetic styling and punchy cinema audio.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}

    ffmpeg_bin = get_ffmpeg_path()
    if not output_dir:
        output_dir = os.path.join(PROJECT_DIR, "data", "processed_shorts")
    os.makedirs(output_dir, exist_ok=True)

    info = get_video_info(input_path, ffmpeg_bin)
    duration = info.get("duration", 0)
    has_audio = info.get("has_audio", False)
    width = info.get("width", 1920)
    height = info.get("height", 1080)
    clip_duration = min(duration, max_duration) if duration > 0 else max_duration

    filter_complex, style_name = build_adaptive_filter(width, height, clip_duration, style_index=style_index)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    raw_hash = hashlib.sha256(f"{base_name}_{clip_duration}_{style_name}".encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"short_{timestamp}_{raw_hash}.mp4"
    out_path = os.path.join(output_dir, out_filename)

    # Check for available background music (BGM) in data/bgm/ if audio is missing
    import glob
    bgm_candidates = glob.glob(os.path.join(PROJECT_DIR, "data", "bgm", "*.mp3")) + \
                     glob.glob(os.path.join(PROJECT_DIR, "data", "bgm", "*.m4a")) + \
                     glob.glob(os.path.join(PROJECT_DIR, "data", "bgm", "*.wav"))
    selected_bgm = bgm_candidates[0] if bgm_candidates else None

    cmd = [ffmpeg_bin, "-y", "-ss", "0", "-t", str(clip_duration), "-i", input_path]

    # Punchy audio enhancement: bass boost for impacts, treble clarity, dynamic volume
    audio_filters = "atempo=1.04,volume=1.06,bass=g=5:f=110,treble=g=3:f=3500"

    if has_audio:
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a",
            "-af", audio_filters
        ])
    elif selected_bgm:
        print(f"[*] Input video has no audio. Auto-mixing background music: {os.path.basename(selected_bgm)}", file=sys.stderr)
        cmd.extend([
            "-stream_loop", "-1",
            "-ss", "0",
            "-t", str(clip_duration),
            "-i", selected_bgm,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a",
            "-af", f"{audio_filters},volume=0.9"
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]"
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",  # Visually lossless master grade
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-movflags", "+faststart",
        out_path
    ])

    print(f"[*] Rendering anime short with style [{style_name}]: {os.path.basename(input_path)} ...", file=sys.stderr)
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
        "editing_style": style_name,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ffmpeg_generator.py <input_video_path> [output_dir] [max_duration] [style_index]")
        sys.exit(1)

    inp = sys.argv[1]
    out_d = sys.argv[2] if len(sys.argv) > 2 else None
    max_d = float(sys.argv[3]) if len(sys.argv) > 3 else 58
    s_idx = int(sys.argv[4]) if len(sys.argv) > 4 else None

    res = generate_short(inp, output_dir=out_d, max_duration=max_d, style_index=s_idx)
    print(json.dumps(res, indent=2))
