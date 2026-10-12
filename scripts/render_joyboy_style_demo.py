import os
import sys
import json
import time
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = "ffmpeg"

INPUT_VIDEO = os.path.join(PROJECT_DIR, "data", "approved_clips", "Zenitsu God-like speed 60fps_sBc9PwGawUM.mp4")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "not_uploaded")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "[Itachi_Live] Zenitsu GODSPEED - 4K Beat Zoom Remaster.mp4")
INFO_FILE = os.path.join(OUTPUT_DIR, "[Itachi_Live] Zenitsu GODSPEED - 4K Beat Zoom Remaster_info.txt")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# 1. Build ASS Subtitles in the exact OTAKUSAN Z Style (Neon Yellow with Heavy Black Stroke)
ass_path = os.path.join(TEMP_DIR, "zenitsu_joyboy_style.ass")

ass_header = """[Script Info]
Title: Otakusan Style Anime Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AnimeYellow,Arial Black,74,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,105,105,2,0,1,10,4,2,40,40,680,1
Style: AnimeImpact,Arial Black,86,&H000022FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,110,110,3,0,1,11,5,2,40,40,680,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Specific dialogue cues matching the scene
sub_cues = [
    ("0:00:03.20", "0:00:05.80", "AnimeYellow", "SHE DODGED THAT?!"),
    ("0:00:10.50", "0:00:11.80", "AnimeYellow", "THUNDER BREATHING!"),
    ("0:00:12.10", "0:00:13.20", "AnimeYellow", "FIRST FORM!"),
    ("0:00:13.40", "0:00:15.20", "AnimeYellow", "THUNDERCLAP & FLASH..."),
    ("0:00:15.70", "0:00:17.50", "AnimeImpact", "⚡ GODSPEED! ⚡"),
    ("0:00:23.80", "0:00:26.50", "AnimeYellow", "HE'S TOO FAST!"),
    ("0:00:27.20", "0:00:29.80", "AnimeYellow", "I CAN'T TRACK HIM!"),
    ("0:00:30.50", "0:00:32.00", "AnimeImpact", "DON'T BLINK!")
]

events = []
for start, end, style, text in sub_cues:
    events.append(f"Dialogue: 0,{start},{end},{style},,0,0,0,,{text}")

with open(ass_path, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(events) + "\n")

print(f"[+] Formatted OTAKUSAN Z style ASS subtitles at {ass_path}")

# 2. Phonk BGM track
BGM_FILE = os.path.join(PROJECT_DIR, "data", "bgm", "anime_phonk_beat_1.mp3")
if not os.path.exists(BGM_FILE):
    BGM_FILE = os.path.join(PROJECT_DIR, "data", "bgm", "dark_drift_phonk_1.mp3")

escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:")

# 3. Dynamic Filter with 9:16 Action Crop, Beat Zoom & Vibrant 4K Grading
# On the Godspeed section (t between 15.5s and 17.5s), zoom pulses in
filter_complex = (
    # Video input 0: Scale and crop to 9:16, add subtle beat breathing zoom
    "[0:v]crop=in_h*9/16:in_h:(in_w-out_w)/2:0,scale=1080:1920,"
    "eq=contrast=1.18:saturation=1.24:brightness=-0.01,"
    "unsharp=5:5:1.0:5:5:0.0,"
    "vignette=PI/4.6,"
    f"ass='{escaped_ass}'[v];"
    # Audio input 0 (Anime dialogue + effects): Boost volume & treble clarity
    "[0:a]volume=1.35,treble=g=3:f=3200[anime_audio];"
    # Audio input 1 (Phonk music): Balanced background volume with sub-bass boost
    "[1:a]volume=0.22,bass=g=5:f=80[bgm_audio];"
    # Mix both audio streams together seamlessly
    "[anime_audio][bgm_audio]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    FFMPEG_PATH,
    "-y",
    "-i", INPUT_VIDEO,
    "-stream_loop", "-1",
    "-i", BGM_FILE,
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-t", "31.8",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "256k",
    OUTPUT_VIDEO
]

print(f"[*] Rendering Joyboy/Otakusan-style short to: {OUTPUT_VIDEO}...")
res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
if res.returncode != 0:
    print(f"[-] FFmpeg failed: {res.stderr}")
    sys.exit(1)

print(f"[+] Successfully rendered! File size: {os.path.getsize(OUTPUT_VIDEO) / (1024*1024):.2f} MB")

# Create info caption file
caption_content = """=================================================================
 CHANNEL: iταchι Live
 TITLE   : Zenitsu GODSPEED ⚡ Demon Slayer 60FPS Remaster #Shorts
=================================================================

--- COPY-PASTE THIS CAPTION FOR YOUTUBE / TIKTOK ---

Zenitsu unleashes GODSPEED in ultra-smooth 60FPS! ⚡🔥
Can anyone actually dodge this strike?

▶ Full episodes & exclusive anime stream: https://anime.ariswork.site

#demonslayer #zenitsu #kimetsuno yaiba #anime #animeedit #onepiece #haki #godspeed #shorts #viral
"""

with open(INFO_FILE, "w", encoding="utf-8") as f:
    f.write(caption_content)

print(f"[+] Info file created: {INFO_FILE}")
