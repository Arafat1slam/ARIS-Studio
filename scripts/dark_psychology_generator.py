import os
import sys
import json
import time
import hashlib
import asyncio
import subprocess
import shutil
import edge_tts
from datetime import datetime
from dotenv import load_dotenv

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

load_dotenv(os.path.join(PROJECT_DIR, ".env"))
import duplicate_checker
import publish_channel2

FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
BGM_FILE = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")

os.makedirs(BROLL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Curated High-Engagement Psychological Scripts for ArisVexx
PRESET_SCRIPTS = [
    {
        "title": "When Someone Goes Silent... Dark Psychology",
        "badge": "WARNING: DARK PSYCHOLOGY",
        "lines": [
            ("Look closely...", "Gold"),
            ("When someone goes completely silent...", "Red"),
            ("They have already made their decision.", "Gold"),
            ("Rule one: Never react to disrespect.", "Gold"),
            ("Your silence cuts deeper than anger.", "Red"),
            ("Rule two: Keep your moves invisible.", "Gold"),
            ("People cannot destroy what they cannot see.", "Normal"),
            ("Rule three is the most dangerous.", "Red"),
            ("Watch their eyes... not their lips.", "Gold"),
            ("The eyes never know how to lie.", "Red")
        ]
    },
    {
        "title": "The Art of Silence (Law 4) | Dark Psychology",
        "badge": "LAW 4: SAY LESS THAN NECESSARY",
        "lines": [
            ("Stop explaining yourself.", "Red"),
            ("The more you speak...", "Normal"),
            ("The more ordinary you appear.", "Gold"),
            ("Powerful people impress by saying less.", "Normal"),
            ("Silence makes people uncomfortable.", "Gold"),
            ("They will rush to fill the void...", "Normal"),
            ("And reveal their true intentions.", "Red"),
            ("Control your tongue...", "Gold"),
            ("Or they will control your life.", "Red"),
            ("Master the silence.", "Gold")
        ]
    },
    {
        "title": "How to Read Anyone in 3 Seconds | Psychology",
        "badge": "HOW TO READ ANYONE",
        "lines": [
            ("Want to know if they are lying?", "Red"),
            ("Watch their hands and feet.", "Gold"),
            ("The face can easily fake a smile...", "Normal"),
            ("But the body never forgets the truth.", "Red"),
            ("If they touch their neck...", "Gold"),
            ("They are feeling deeply insecure.", "Normal"),
            ("If they look up and right...", "Gold"),
            ("They are inventing a story.", "Red"),
            ("Never trust words.", "Gold"),
            ("Only trust patterns.", "Red")
        ]
    },
    {
        "title": "Never Reveal Your True Plans | Stoic Rule",
        "badge": "RULE OF INVISIBILITY",
        "lines": [
            ("A private life is a peaceful life.", "Gold"),
            ("Never announce your next big move.", "Red"),
            ("When you share your goals...", "Normal"),
            ("Envy and sabotage begin to whisper.", "Red"),
            ("Work in total silence.", "Gold"),
            ("Let your success make the noise.", "Red"),
            ("Keep them guessing.", "Gold"),
            ("Shock them with the results.", "Red")
        ]
    }
]

def generate_script_with_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        import random
        return random.choice(PRESET_SCRIPTS)

    prompt = (
        "Generate a 25-second viral Dark Psychology / 48 Laws of Power Short script for channel 'ArisVexx'. "
        "Format as JSON with keys:\n"
        "- title: Clickable viral title with #Shorts\n"
        "- badge: Short 3-word warning badge for top of video\n"
        "- lines: List of tuples [text, highlight_color] where color is 'Normal', 'Gold', or 'Red'.\n"
        "Keep total lines between 8 and 10 short, punchy 2-4 word sentences. Maximum intensity."
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    try:
        import urllib.request
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            raw = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw)
    except Exception as e:
        print(f"[!] Gemini generation fallback: {e}", file=sys.stderr)
        import random
        return random.choice(PRESET_SCRIPTS)

async def create_voice_and_timing(lines: list, voice_path: str):
    full_text = " ".join([line[0] for line in lines])
    
    # 1. Try Edge-TTS (up to 4 retries across top neural male voices)
    male_voices = ["en-US-BrianNeural", "en-US-ChristopherNeural", "en-US-GuyNeural"]
    for attempt in range(1, 5):
        chosen_voice = male_voices[(attempt - 1) % len(male_voices)]
        try:
            print(f"[*] Generating deep male voiceover via Edge-TTS ({chosen_voice}, Attempt {attempt}/4)...", file=sys.stderr)
            communicate = edge_tts.Communicate(full_text, voice=chosen_voice, rate="-3%", pitch="-1Hz")
            cues = []
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    s = chunk["offset"] / 10000000
                    d = chunk["duration"] / 10000000
                    cues.append((s, s + d, chunk["text"].strip()))
            
            if audio_data and cues:
                with open(voice_path, "wb") as f:
                    f.write(audio_data)
                print(f"[+] Edge-TTS deep male voice generated successfully ({len(cues)} cues).", file=sys.stderr)
                return cues
        except Exception as e:
            print(f"[!] Edge-TTS attempt {attempt} failed: {e}", file=sys.stderr)
            await asyncio.sleep(2 * attempt)

    # 2. Resilient Deep-Male Pitch-Shifted Fallback (NEVER female!)
    print("[!] Transforming voice into deep baritone male voice...", file=sys.stderr)
    try:
        from gtts import gTTS
        raw_tts = os.path.join(TEMP_DIR, f"raw_tts_{int(time.time())}.mp3")
        tts = gTTS(text=full_text, lang='en', tld='us', slow=False)
        tts.save(raw_tts)
        
        # Pitch-shift by -4 semitones and boost sub-bass to create authoritative deep male narrator
        shift_cmd = [
            FFMPEG_PATH, "-y", "-i", raw_tts,
            "-af", "asetrate=24000*0.78,atempo=1.28,bass=g=8,volume=1.25",
            voice_path
        ]
        subprocess.run(shift_cmd, check=True)
        try: os.remove(raw_tts)
        except: pass

        from broll_manager import get_video_duration
        total_dur = get_video_duration(voice_path)
        if total_dur <= 0:
            total_dur = 22.0
            
        total_chars = max(1, sum(len(line[0]) for line in lines))
        curr_time = 0.1
        cues = []
        for line in lines:
            txt = line[0]
            fraction = len(txt) / total_chars
            dur = max(1.2, fraction * (total_dur - 0.4))
            cues.append((curr_time, curr_time + dur, txt))
            curr_time += dur
            
        print(f"[+] Deep baritone voice generated ({total_dur:.1f}s, {len(cues)} cues).", file=sys.stderr)
        return cues
    except Exception as e:
        print(f"[-] Voice fallback failed: {e}", file=sys.stderr)
        raise RuntimeError(f"All TTS engines failed: {e}")

def format_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{ms:02d}"

def build_ass_subtitles(badge: str, lines: list, cues: list, ass_path: str):
    header = """[Script Info]
Title: ArisVexx Viral Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Normal,Arial Black,64,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,7,5,2,40,40,820,1
Style: Gold,Arial Black,68,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,106,106,2,0,1,8,6,2,40,40,820,1
Style: Red,Arial Black,70,&H002222FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,108,108,2,0,1,8,6,2,40,40,820,1
Style: Badge,Arial Black,34,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,3,0,1,5,3,2,40,40,1650,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    # Badge for first 3.5s
    dialogues.append(f"Dialogue: 0,0:00:00.05,0:00:03.50,Badge,,0,0,0,,{badge}")
    
    # Map lines to cues
    total = min(len(lines), len(cues))
    for i in range(total):
        start_sec, end_sec, _ = cues[i]
        text, style = lines[i]
        s_str = format_ass_time(start_sec)
        e_str = format_ass_time(end_sec)
        clean_text = text.upper().replace('"', '').replace("'", "")
        dialogues.append(f"Dialogue: 0,{s_str},{e_str},{style},,0,0,0,,{clean_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues) + "\n")

def produce_arisvexx_short(dry_run: bool = False) -> dict:
    timestamp = int(time.time())
    print("\n" + "="*65)
    print("   ARISVEXX AUTOMATION ENGINE - PRODUCING DARK PSYCHOLOGY SHORT")
    print("="*65)

    # 1. Generate Script
    script_data = generate_script_with_ai()
    title = script_data.get("title", "The Rules of Power | Dark Psychology")
    badge = script_data.get("badge", "DARK PSYCHOLOGY")
    lines = script_data.get("lines", [])
    print(f"[*] Title: {title}")
    print(f"[*] Badge: {badge}")

    # 2. Generate Voice & Timestamps
    voice_file = os.path.join(TEMP_DIR, f"voice_{timestamp}.mp3")
    print("[*] Generating neural voiceover & boundary timings...")
    cues = asyncio.run(create_voice_and_timing(lines, voice_file))

    # 3. Build ASS Subtitles
    ass_file = os.path.join(TEMP_DIR, f"subs_{timestamp}.ass")
    build_ass_subtitles(badge, lines, cues, ass_file)
    print("[*] Formatted dynamic ASS subtitles.")

    # 4. Source Dynamic Unique B-Roll
    import broll_manager
    broll_source, broll_offset = broll_manager.get_unique_broll(segment_duration=28)
    print(f"[*] Applying unique B-Roll scene: {os.path.basename(broll_source)} (Offset: {broll_offset}s)")

    # 5. Master Render with FFmpeg (Cinematic Vignette, 4K Sharpness, Color Grading)
    output_video = os.path.join(OUTPUT_DIR, f"arisvexx_{timestamp}.mp4")
    escaped_ass = ass_file.replace("\\", "/").replace(":", r"\:")

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.20:brightness=-0.03:saturation=0.90,"
        "vignette=PI/4.5,"
        "unsharp=3:3:0.9,"
        f"ass='{escaped_ass}',"
        "drawtext=text='ARISVEXX':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=180:shadowcolor=black:shadowx=3:shadowy=3,"
        "drawtext=text='THE 48 LAWS OF POWER':fontsize=22:fontcolor=0xff2244:x=(w-text_w)/2:y=230:shadowcolor=black:shadowx=2:shadowy=2[v];"
        "[1:a]volume=1.30[voice];"
        "[2:a]volume=0.15[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    )

    # Exact video duration based on voiceover to prevent any FFmpeg infinite looping
    voice_dur = cues[-1][1] if cues else 22.0
    target_duration = round(voice_dur + 1.2, 2)
    print(f"[*] Target Short duration: {target_duration}s (Voice: {voice_dur:.1f}s)")

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-ss", str(broll_offset),
        "-stream_loop", "-1",
        "-i", broll_source,
        "-i", voice_file,
        "-stream_loop", "-1",
        "-i", BGM_FILE,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-t", str(target_duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video
    ]

    print("[*] Rendering video canvas with strict duration limit...")
    subprocess.run(cmd, check=True)
    print(f"[+] Video rendered successfully: {os.path.basename(output_video)} ({os.path.getsize(output_video)/(1024*1024):.2f} MB)")

    # 6. Compute Hash
    with open(output_video, "rb") as f:
        c_hash = hashlib.sha256(f.read()).hexdigest()

    # 7. Check Duplicate
    is_dup, _ = duplicate_checker.is_duplicate(c_hash)
    if is_dup:
        print("[!] Duplicate detected in ledger, skipping upload.")
        return {"status": "duplicate_skipped"}

    # 8. Publish to ArisVexx
    desc = (
        f"{title}\n\n"
        "Welcome to ArisVexx. We decode human psychology, power dynamics, and stoic principles.\n\n"
        "#darkpsychology #lawsofpower #stoic #mindset #arisvexx #sigmarules #psychologyfacts #shorts"
    )
    pub_res = publish_channel2.publish_to_channel2(
        video_path=output_video,
        title=title,
        description=desc,
        dry_run=dry_run
    )

    # 9. Record in Ledger
    record = {
        "content_hash": c_hash,
        "video_file": os.path.basename(output_video),
        "title": title,
        "channel": "ArisVexx",
        "published_at": datetime.utcnow().isoformat() + "Z",
        "youtube_id": pub_res.get("video_id"),
        "status": "published"
    }
    duplicate_checker.add_record(record)

    # 10. Archive to 'uploaded/' folder for preview or manual posting
    try:
        import archive_uploaded_videos
        archive_uploaded_videos.save_to_uploaded_archive(
            video_path=output_video,
            title=title,
            description=desc,
            tags=["darkpsychology", "lawsofpower", "stoic", "mindset", "arisvexx", "sigmarules", "psychologyfacts", "shorts"],
            channel="ArisVexx",
            move=False if dry_run else True
        )
    except Exception as e:
        print(f"[-] Archive notice: {e}")
        try:
            if os.path.exists(output_video) and not dry_run:
                os.remove(output_video)
        except Exception:
            pass

    # Clean temps
    for t_file in [voice_file, ass_file]:
        if os.path.exists(t_file):
            try: os.remove(t_file)
            except: pass

    return {
        "status": "completed",
        "title": title,
        "channel": "ArisVexx",
        "youtube_url": pub_res.get("video_url"),
        "details": pub_res
    }

if __name__ == "__main__":
    cfg_review = True
    try:
        with open(os.path.join(PROJECT_DIR, "config", "config.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)
            cfg_review = cfg.get("pipeline", {}).get("review_gate_enabled", True)
    except Exception:
        pass
    force_auto = "--auto" in sys.argv
    is_dry = "--dry-run" in sys.argv or (cfg_review and not force_auto)
    res = produce_arisvexx_short(dry_run=is_dry)
    print(json.dumps(res, indent=2))
