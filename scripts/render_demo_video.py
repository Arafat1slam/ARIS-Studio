import os
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)

video_in = os.path.join(PROJECT_DIR, "data", "temp", "shelby_raw.webm")
voice_in = os.path.join(PROJECT_DIR, "data", "temp", "demo_voice.mp3")
bgm_in = os.path.join(PROJECT_DIR, "data", "bgm", "anime_phonk_beat_1.mp3")
ass_path = os.path.join(PROJECT_DIR, "data", "temp", "demo_subs.ass")
out_file = os.path.join(PROJECT_DIR, "data", "processed_shorts", "arisvexx_dark_psychology_demo.mp4")

os.makedirs(os.path.dirname(out_file), exist_ok=True)

# Escape backslashes and colons for ffmpeg filter string on Windows
escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:")

filter_complex = (
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    "eq=contrast=1.18:brightness=-0.02:saturation=0.9,"
    f"ass='{escaped_ass}',"
    "drawtext=text='ARISVEXX':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=180:shadowcolor=black:shadowx=3:shadowy=3,"
    "drawtext=text='DARK PSYCHOLOGY':fontsize=28:fontcolor=0xff2244:x=(w-text_w)/2:y=240:shadowcolor=black:shadowx=2:shadowy=2[v];"
    "[1:a]volume=1.2[voice];"
    "[2:a]volume=0.15[bgm];"
    "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    "tools/ffmpeg.exe",
    "-y",
    "-stream_loop", "-1",
    "-i", video_in,
    "-i", voice_in,
    "-stream_loop", "-1",
    "-i", bgm_in,
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "19",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    out_file
]

print("[*] Starting master FFmpeg render for ArisVexx demo Short...")
proc = subprocess.run(cmd, capture_output=True, text=True)

if proc.returncode != 0:
    print(f"[-] FFmpeg render failed:\n{proc.stderr[-600:]}")
else:
    size_mb = os.path.getsize(out_file) / (1024 * 1024)
    print(f"[SUCCESS] Demo video rendered successfully! Size: {size_mb:.2f} MB")
    print(f"[PATH] {out_file}")
