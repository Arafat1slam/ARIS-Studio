"""
FFmpeg Shorts / Reels Generator for ARIS Content Automation System (Channel 1: iταchι Live).
Transforms anime clips into stunning 9:16 vertical Shorts/Reels (<= 58s).

Signature Aesthetic (As featured in the first uploaded viral videos):
- Dark Ambient Spotlight Remaster:
    - Background: 1080x1920 vertical canvas with ambient blurred anime backdrop and vignette
    - Foreground: Full 16:9 widescreen anime frame centered, razor-sharp 4K contrast and saturation
    - 100% Clean Visuals: ZERO artificial text or subtitles blocking the animation!
- Movie-theater audio enhancement:
    - 1.04x micro-tempo shift (anti-copyright signature)
    - Punchy bass EQ (+5dB @ 110Hz) for impacts and sword clashes
    - Crisp treble (+3dB @ 3500Hz) for voice lines and crystal clear sound effects
- Strict <= 58s duration cap for Shorts/Reels compliance
"""

import os
import sys
import glob
import json
import random
import re
import subprocess
import hashlib
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
BGM_DIR = os.path.join(PROJECT_DIR, "data", "bgm")

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
    Constructs high-aesthetic FFmpeg filter graphs based on aspect ratio and style.
    Default (style_index=0 or None) is the iconic DARK_AMBIENT_SPOTLIGHT featured in the first uploaded videos!
    """
    is_already_vertical = height > int(width * 1.2)

    if is_already_vertical:
        style_name = "NATIVE_VERTICAL_4K"
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=contrast=1.12:saturation=1.20:brightness=0.01,"
            "unsharp=5:5:0.8:5:5:0.0,vignette=PI/4.5,setpts=PTS/1.04[v]"
        )
        return filter_complex, style_name

    # Styles for widescreen 16:9 video
    # 0 = ACTION_FULLSCREEN_916 (Center crop full bleed - Otakusan Joyboy Style - NO black bars)
    # 1 = DARK_AMBIENT_SPOTLIGHT (Dynamic ambient motion background - NO black bars)
    styles = [
        (
            "ACTION_FULLSCREEN_916",
            (
                "[0:v]crop=in_h*9/16:in_h:(in_w-out_w)/2:0,scale=1080:1920,"
                "eq=contrast=1.18:saturation=1.24:brightness=-0.01,"
                "unsharp=5:5:1.0:5:5:0.0,vignette=PI/4.6,setpts=PTS/1.04[v]"
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
        style_index = 0  # Default to ACTION_FULLSCREEN_916 (Otakusan Joyboy style)
    else:
        style_index = style_index % len(styles)

    chosen_style, filter_str = styles[style_index]
    return filter_str, chosen_style

def generate_short(input_path, output_dir=None, max_duration=58, style_index=0):
    """
    Process an anime clip into clean vertical 9:16 Short/Reel format with high-aesthetic styling
    and punchy cinema audio. Zero artificial text overlays.
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
    bgm_candidates = glob.glob(os.path.join(BGM_DIR, "*phonk*.mp3")) + \
                     glob.glob(os.path.join(BGM_DIR, "*.mp3"))
    selected_bgm = bgm_candidates[0] if bgm_candidates else None

    cmd = [ffmpeg_bin, "-y", "-ss", "0", "-t", str(clip_duration), "-i", input_path]

    # Movie-theater audio enhancement: punchy bass EQ for impacts, crisp treble clarity
    audio_filters = "atempo=1.04,volume=1.08,bass=g=5:f=110,treble=g=3:f=3500"

    # Anti-copyright defense: Mix anime dialogue with trending background Phonk beats
    if has_audio and selected_bgm:
        print(f"[*] Applying anti-copyright Phonk BGM layer ({os.path.basename(selected_bgm)}) to anime audio...", file=sys.stderr)
        cmd.extend([
            "-stream_loop", "-1",
            "-i", selected_bgm,
            "-filter_complex", (
                f"{filter_complex};"
                "[0:a]volume=1.30,treble=g=3:f=3200[anime_audio];"
                "[1:a]volume=0.22,bass=g=5:f=80[bgm_audio];"
                "[anime_audio][bgm_audio]amix=inputs=2:duration=first:dropout_transition=2[a]"
            ),
            "-map", "[v]",
            "-map", "[a]"
        ])
    elif has_audio:
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
            "-ss", "0", "-t", str(clip_duration),
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
        "created_at": datetime.now().isoformat() + "Z"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ffmpeg_generator.py <input_video_path> [output_dir] [max_duration] [style_index]")
        sys.exit(1)

    inp = sys.argv[1]
    out_d = sys.argv[2] if len(sys.argv) > 2 else None
    max_d = float(sys.argv[3]) if len(sys.argv) > 3 else 58
    s_idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    res = generate_short(inp, output_dir=out_d, max_duration=max_d, style_index=s_idx)
    print(json.dumps(res, indent=2))
