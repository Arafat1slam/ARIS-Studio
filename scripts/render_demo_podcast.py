import os
import sys
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
INPUT_VIDEO = os.path.join(PROJECT_DIR, "data", "temp", "robert_greene_dark_side_merged.mp4")
BGM = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")
OUTPUT_VIDEO = os.path.join(PROJECT_DIR, "uploaded", "[ArisVexx] The Power of Your Dark Side - Robert Greene.mp4")
INFO_TXT = os.path.join(PROJECT_DIR, "uploaded", "[ArisVexx] The Power of Your Dark Side - Robert Greene_info.txt")

os.makedirs(os.path.dirname(OUTPUT_VIDEO), exist_ok=True)

# Using font Arial
filter_complex = (
    "[0:v]eq=contrast=1.12:saturation=1.15:brightness=0.01,unsharp=3:3:0.8,vignette=PI/4.5,"
    "drawbox=x=0:y=160:w=1080:h=95:color=black@0.72:t=fill,"
    "drawtext=font='Arial':text='ROBERT GREENE | LAWS OF POWER':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=190,"
    "drawtext=font='Arial':text='@ArisVexx':fontcolor=white@0.65:fontsize=28:x=(w-text_w)/2:y=1740[v];"
    "[0:a]volume=1.22,bass=g=4:f=120[voice];"
    "[1:a]volume=0.14[bgm];"
    "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    FFMPEG, "-y",
    "-ss", "0", "-t", "41.79",
    "-i", INPUT_VIDEO,
    "-stream_loop", "-1",
    "-ss", "0", "-t", "41.79",
    "-i", BGM,
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    OUTPUT_VIDEO
]

print("[*] Rendering Robert Greene Podcast Short via FFmpeg...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
if res.returncode != 0:
    print("[-] FFmpeg Error:", res.stderr)
    sys.exit(1)

print("[+] Successfully rendered:", OUTPUT_VIDEO)

# Create companion info text
caption_text = """=================================================================
 CHANNEL: ArisVexx
 TITLE   : The Power of Your Dark Side | Robert Greene #Shorts
=================================================================

--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK / YOUTUBE ---

The Power of Your Dark Side | Robert Greene #Shorts

"Never suppress your dark side. Channel it into relentless focus and power." - Robert Greene (Author of 48 Laws of Power)

Speaker: Robert Greene
Topic: Dark Psychology & The 48 Laws of Power

#RobertGreene #DarkPsychology #48LawsOfPower #ArisVexx #Mindset #PowerDynamics #PsychologyFacts #Shorts #PodcastClips

=================================================================
"""

with open(INFO_TXT, "w", encoding="utf-8") as f:
    f.write(caption_text)

print("[+] Created companion info file:", INFO_TXT)
