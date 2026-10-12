"""
FFmpeg Shorts / Reels Generator for ARIS Content Automation System.
Transforms anime clips into stunning 9:16 vertical Shorts/Reels (<= 58s).

Key Features:
- Multi-Style Adaptive Video Engine:
    1. Fullscreen Action 9:16 (Center Crop full bleed - viral TikTok/Shorts style)
    2. Obsidian Cinematic Letterbox (Sleek dark matte theater framing)
    3. Dark Ambient Spotlight (Deep mood lighting backdrop with spotlight vignette)
    4. Native Vertical Remaster (For clips already in 9:16 format)
- High-Energy Phonk BGM Engine:
    - Layering aggressive / drift phonk beats dynamically with anime audio & sound effects
    - Bass boost EQ on phonk drops + treble clarity on sword clashes & combat SFX
- Viral Kinetic Typography & ASS Subtitle Engine:
    - Glowing top hook badge (e.g. ⚡ GODSPEED ⚡, ⚔️ LEVI UNLEASHED ⚔️)
    - High-retention word-highlighted action cues in lower-third
    - Cross-platform font fallback (Windows Arial Black / Linux DejaVu Sans)
- Razor-sharp 4K visual remastering (unsharp mask, rich contrast, dynamic saturation)
- Strict <= 58s duration cap for Shorts/Reels compliance
- Fingerprints output video with SHA-256 hash
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
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
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

def format_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{ms:02d}"

def generate_anime_ass_subtitles(clip_name: str, duration: float, ass_path: str):
    """
    Generates high-retention viral ASS subtitles and kinetic action typography for anime clips.
    Uses bold fonts, neon highlights, and lower-third placement.
    """
    clean_name = clip_name.lower()
    
    # Context-aware Hook Badge
    if "zenitsu" in clean_name:
        badge = "⚡ ZENITSU | GODSPEED ⚡"
        accent_color = "&H0000FFFF"  # Neon Yellow
        cues = [
            (0.0, 3.2, "THUNDER BREATHING"),
            (3.2, 7.0, "FIRST FORM: {\\c&H0000FFFF&}GODSPEED{\\c&H00FFFFFF&} ⚡"),
            (7.0, 11.5, "BEYOND {\\c&H0000FFFF&}HUMAN{\\c&H00FFFFFF&} SPEED"),
            (11.5, 16.0, "DON'T BLINK..."),
            (16.0, 21.0, "{\\c&H0000FFFF&}LIGHTNING{\\c&H00FFFFFF&} FAST ⚡"),
            (21.0, 26.5, "ONE STRIKE, {\\c&H0000FFFF&}ONE KILL{\\c&H00FFFFFF&}"),
            (26.5, 32.0, "ABSOLUTE {\\c&H002222FF&}PERFECTION{\\c&H00FFFFFF&} 🔥"),
            (32.0, duration, "FOLLOW FOR MORE ⚔️")
        ]
    elif "levi" in clean_name or "titan" in clean_name:
        badge = "⚔️ LEVI ACKERMAN | GOD MODE ⚔️"
        accent_color = "&H0000CCFF"  # Bright Amber/Gold
        cues = [
            (0.0, 3.2, "HUMANITY'S STRONGEST SOLDIER"),
            (3.2, 7.0, "{\\c&H0000CCFF&}LEVI ACKERMAN{\\c&H00FFFFFF&} ⚔️"),
            (7.0, 11.5, "VS THE ANCIENT TITANS"),
            (11.5, 16.0, "{\\c&H002222FF&}ABSOLUTE{\\c&H00FFFFFF&} GOD MODE 🔥"),
            (16.0, 21.0, "SPEED AND PRECISION"),
            (21.0, 26.0, "DON'T BLINK..."),
            (26.0, duration, "FOLLOW FOR MORE ⚔️")
        ]
    elif "gojo" in clean_name or "jujutsu" in clean_name:
        badge = "🔥 SATORU GOJO | DOMAIN EXPANSION 🔥"
        accent_color = "&H00FFFF00"  # Neon Cyan
        cues = [
            (0.0, 3.2, "THE STRONGEST SORCERER"),
            (3.2, 7.0, "{\\c&H00FFFF00&}SATORU GOJO{\\c&H00FFFFFF&} 🔥"),
            (7.0, 11.5, "LIMITLESS VOID"),
            (11.5, 16.0, "{\\c&H002222FF&}INFINITY{\\c&H00FFFFFF&} UNLEASHED"),
            (16.0, 21.0, "DON'T BLINK..."),
            (21.0, 26.0, "ABSOLUTE DOMINATION"),
            (26.0, duration, "FOLLOW FOR MORE ⚔️")
        ]
    elif "sukuna" in clean_name:
        badge = "🔥 RYOMEN SUKUNA | KING OF CURSES 🔥"
        accent_color = "&H002222FF"  # Crimson Red
        cues = [
            (0.0, 3.2, "KING OF CURSES"),
            (3.2, 7.0, "{\\c&H002222FF&}MALEVOLENT SHRINE{\\c&H00FFFFFF&} 🔥"),
            (7.0, 11.5, "CLEAVE AND DISMANTLE"),
            (11.5, 16.0, "NO MERCY..."),
            (16.0, 21.0, "ABSOLUTE POWER"),
            (21.0, duration, "FOLLOW FOR MORE ⚔️")
        ]
    else:
        badge = "🔥 ANIME TRANSCENDENCE 4K 🔥"
        accent_color = "&H0000FFFF"  # Neon Yellow
        cues = [
            (0.0, 3.2, "WATCH TILL THE END"),
            (3.2, 7.0, "UNLEASHING {\\c&H0000FFFF&}FULL POWER{\\c&H00FFFFFF&} 🔥"),
            (7.0, 11.5, "THE MOST {\\c&H002222FF&}INSANE{\\c&H00FFFFFF&} MOMENT"),
            (11.5, 16.0, "DON'T BLINK..."),
            (16.0, 21.0, "TRANSCENDING {\\c&H0000FFFF&}LIMITS{\\c&H00FFFFFF&} ⚡"),
            (21.0, 26.0, "FEEL THE ADRENALINE 🔥"),
            (26.0, duration, "FOLLOW FOR MORE ⚔️")
        ]

    header = f"""[Script Info]
Title: Anime Viral Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AnimeMain,Arial Black,70,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,8,4,2,40,40,740,1
Style: AnimeHook,Arial Black,34,{accent_color},&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,3,0,1,6,3,2,40,40,1660,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    # Badge for first 4.5 seconds
    dialogues.append(f"Dialogue: 0,0:00:00.05,0:00:04.50,AnimeHook,,0,0,0,,{badge}")

    for s_time, e_time, text in cues:
        if s_time >= duration:
            break
        e_clamped = min(e_time, duration)
        if e_clamped <= s_time:
            continue
        s_str = format_ass_time(s_time)
        e_str = format_ass_time(e_clamped)
        dialogues.append(f"Dialogue: 0,{s_str},{e_str},{'AnimeMain'},,0,0,0,,{text}")

    os.makedirs(os.path.dirname(ass_path), exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues) + "\n")

def get_phonk_track():
    """Selects a trending high-energy phonk music track from data/bgm/."""
    candidates = glob.glob(os.path.join(BGM_DIR, "*phonk*.mp3")) + \
                 glob.glob(os.path.join(BGM_DIR, "*beat*.mp3"))
    if not candidates:
        candidates = glob.glob(os.path.join(BGM_DIR, "*.mp3"))
    if candidates:
        return random.choice(candidates)
    return None

def build_adaptive_filter(width, height, clip_duration, style_index=None):
    """
    Constructs high-aesthetic, diverse FFmpeg filter graphs based on aspect ratio and style.
    Guarantees every video has a distinct visual personality!
    Outputs stream '[v_base]'.
    """
    is_already_vertical = height > int(width * 1.2)

    if is_already_vertical:
        # Native vertical format - full bleed 4K remaster
        style_name = "NATIVE_VERTICAL_4K"
        filter_base = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=contrast=1.12:saturation=1.22:brightness=0.01,"
            "unsharp=5:5:0.8:5:5:0.0,vignette=PI/4.5,setpts=PTS/1.04[v_base]"
        )
        return filter_base, style_name

    # For horizontal / 16:9 widescreen video, offer 3 diverse editing styles:
    styles = [
        (
            "ACTION_FULLSCREEN_916",
            (
                "[0:v]crop=in_h*9/16:in_h:(in_w-out_w)/2:0,scale=1080:1920,"
                "eq=contrast=1.15:saturation=1.25:brightness=0.01,"
                "unsharp=5:5:1.0:5:5:0.0,vignette=PI/4.4,setpts=PTS/1.04[v_base]"
            )
        ),
        (
            "CINEMATIC_OBSIDIAN_THEATER",
            (
                f"color=c=0x0a0c14:s=1080x1920:d={clip_duration:.2f}[bg];"
                "[0:v]scale=1080:-2,eq=contrast=1.12:saturation=1.20:brightness=0.01,unsharp=5:5:0.9[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,setpts=PTS/1.04[v_base]"
            )
        ),
        (
            "DARK_AMBIENT_SPOTLIGHT",
            (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "boxblur=42:6,eq=brightness=-0.42:contrast=1.35:saturation=1.45[bg];"
                "[0:v]crop=in_w*0.96:in_h*0.96,scale=1080:-2,eq=contrast=1.10:saturation=1.18,unsharp=5:5:0.8[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,vignette=PI/4.2,setpts=PTS/1.04[v_base]"
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
    Process an anime clip into vertical 9:16 Short/Reel format with high-aesthetic styling,
    trending Phonk music, and viral kinetic typography subtitles.
    """
    if not os.path.exists(input_path):
        return {"success": False, "error": f"Input file not found: {input_path}"}

    ffmpeg_bin = get_ffmpeg_path()
    if not output_dir:
        output_dir = os.path.join(PROJECT_DIR, "data", "processed_shorts")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    info = get_video_info(input_path, ffmpeg_bin)
    duration = info.get("duration", 0)
    has_audio = info.get("has_audio", False)
    width = info.get("width", 1920)
    height = info.get("height", 1080)
    clip_duration = min(duration, max_duration) if duration > 0 else max_duration

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    raw_hash = hashlib.sha256(f"{base_name}_{clip_duration}_{style_index}".encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"short_{timestamp}_{raw_hash}.mp4"
    out_path = os.path.join(output_dir, out_filename)

    # 1. Generate Kinetic ASS Subtitles
    ass_path = os.path.join(TEMP_DIR, f"anime_sub_{raw_hash}.ass")
    generate_anime_ass_subtitles(base_name, clip_duration, ass_path)
    escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:")

    # 2. Build Video Filter Graph with Subtitle Burn-In
    base_filter, style_name = build_adaptive_filter(width, height, clip_duration, style_index=style_index)
    video_filter = f"{base_filter};[v_base]ass='{escaped_ass}'[v]"

    # 3. Phonk Background Music Selection & Audio Mixing
    selected_phonk = get_phonk_track()
    cmd = [ffmpeg_bin, "-y", "-ss", "0", "-t", str(clip_duration), "-i", input_path]

    if selected_phonk:
        print(f"[*] Layering Trending Phonk Beat: {os.path.basename(selected_phonk)}", file=sys.stderr)
        cmd.extend([
            "-stream_loop", "-1",
            "-ss", "0", "-t", str(clip_duration),
            "-i", selected_phonk
        ])

        if has_audio:
            # Layer Anime Audio (SFX + Screams) with heavy Phonk Bass Beat
            audio_filter = (
                "[0:a]atempo=1.04,volume=1.20,treble=g=3:f=3200[sfx];"
                "[1:a]volume=0.38,bass=g=5:f=90[phonk];"
                "[sfx][phonk]amix=inputs=2:duration=first:dropout_transition=2[a]"
            )
            cmd.extend([
                "-filter_complex", f"{video_filter};{audio_filter}",
                "-map", "[v]",
                "-map", "[a]"
            ])
        else:
            # Full Phonk audio if source was silent
            audio_filter = "[1:a]volume=1.0,bass=g=4:f=90[a]"
            cmd.extend([
                "-filter_complex", f"{video_filter};{audio_filter}",
                "-map", "[v]",
                "-map", "[a]"
            ])
    else:
        # Fallback to pure original audio enhancement if no BGM available
        if has_audio:
            cmd.extend([
                "-filter_complex", video_filter,
                "-map", "[v]",
                "-map", "0:a",
                "-af", "atempo=1.04,volume=1.10,bass=g=5:f=110,treble=g=3:f=3500"
            ])
        else:
            cmd.extend([
                "-filter_complex", video_filter,
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

    print(f"[*] Rendering Anime Short [{style_name}] with Phonk & Kinetic Subtitles: {os.path.basename(input_path)} ...", file=sys.stderr)
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
        "phonk_track": os.path.basename(selected_phonk) if selected_phonk else None,
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
