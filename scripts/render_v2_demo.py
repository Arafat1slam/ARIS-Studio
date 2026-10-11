import os
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)

video_in = os.path.join(PROJECT_DIR, "data", "temp", "shelby_full.mp4")
voice_in = os.path.join(PROJECT_DIR, "data", "temp", "v2_voice.mp3")
bgm_in = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")
ass_path = os.path.join(PROJECT_DIR, "data", "temp", "v2_subs.ass")
out_file = os.path.join(PROJECT_DIR, "data", "processed_shorts", "arisvexx_dark_psychology_v2.mp4")

os.makedirs(os.path.dirname(out_file), exist_ok=True)

escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:")

# Filter complex:
# 1. Video: 1080x1920 vertical crop, HDR contrast, subtle unsharp for crispness, vignette, and styled ASS captions
# 2. Audio: Voice volume boosted, BGM gentle at 0.14, clean mix without any old video audio
filter_complex = (
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    "eq=contrast=1.16:brightness=-0.02:saturation=0.92,"
    "unsharp=3:3:0.8,"
    f"ass='{escaped_ass}',"
    "drawtext=text='ARISVEXX':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=180:shadowcolor=black:shadowx=3:shadowy=3,"
    "drawtext=text='THE 48 LAWS OF POWER':fontsize=22:fontcolor=0xff2244:x=(w-text_w)/2:y=230:shadowcolor=black:shadowx=2:shadowy=2[v];"
    "[1:a]volume=1.25[voice];"
    "[2:a]volume=0.14[bgm];"
    "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    "tools/ffmpeg.exe",
    "-y",
    "-ss", "00:00:00",
    "-i", video_in,
    "-i", voice_in,
    "-ss", "00:00:00",
    "-i", bgm_in,
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    out_file
]

print("[*] Starting high-fidelity render for ArisVexx V2 Dark Psychology Short...")
proc = subprocess.run(cmd, capture_output=True, text=True)

if proc.returncode != 0:
    print(f"[-] FFmpeg render failed:\n{proc.stderr[-600:]}")
else:
    size_mb = os.path.getsize(out_file) / (1024 * 1024)
    print(f"[SUCCESS] V2 Master Short rendered! Size: {size_mb:.2f} MB")
    print(f"[PATH] {out_file}")
