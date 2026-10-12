import os
import sys
import json
import time
import hashlib
import asyncio
import subprocess
import shutil
import edge_tts
import urllib.request
import base64
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

def generate_gemini_tts(text: str, voice_name: str = "Charon") -> bytes:
    import base64
    import urllib.error
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY for Gemini TTS")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "response_modalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if not candidates or "content" not in candidates[0]:
                raise RuntimeError(f"Gemini API returned no content candidates: {res}")
            raw_b64 = candidates[0]["content"]["parts"][0]["inlineData"]["data"]
            return base64.b64decode(raw_b64)
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8", errors="ignore") if he.fp else ""
        print(f"[-] Gemini TTS HTTP {he.code} Error: {body}", file=sys.stderr, flush=True)
        raise RuntimeError(f"Gemini TTS HTTP {he.code}: {body}") from he

async def create_voice_and_timing(lines: list, voice_path: str):
    full_text = " ".join([line[0] for line in lines])
    
    # 1. Primary: Edge-TTS BrianNeural (Natural human narrator)
    target_voice = "en-US-BrianNeural"
    for attempt in range(1, 3):
        try:
            print(f"[*] Generating signature natural male voiceover via Edge-TTS ({target_voice}, Attempt {attempt}/2)...", file=sys.stderr)
            communicate = edge_tts.Communicate(full_text, voice=target_voice, rate="-2%")
            cues = []
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    s = chunk["offset"] / 10000000
                    d = chunk["duration"] / 10000000
                    cues.append((s, s + d, chunk["text"].strip()))
            
            if audio_data:
                with open(voice_path, "wb") as f:
                    f.write(audio_data)
                
                if not cues:
                    from broll_manager import get_video_duration
                    total_dur = get_video_duration(voice_path) or 20.0
                    total_chars = max(1, sum(len(line[0]) for line in lines))
                    curr_time = 0.1
                    for line in lines:
                        txt = line[0]
                        fraction = len(txt) / total_chars
                        dur = max(1.2, fraction * (total_dur - 0.4))
                        cues.append((curr_time, curr_time + dur, txt))
                        curr_time += dur

                print(f"[+] BrianNeural signature voice generated successfully ({len(cues)} cues).", file=sys.stderr)
                return cues
        except Exception as e:
            print(f"[!] Edge-TTS attempt {attempt} failed: {e}", file=sys.stderr)
            await asyncio.sleep(1.5)

    # 2. Resilient Cloud-Native Studio Fallback: Google Gemini 2.5 Flash TTS (Charon)
    # 100% natural, deep authoritative male voice. Never blocked on GitHub Actions or cloud IPs!
    print("[*] Sourcing studio-grade deep male narration via Gemini 2.5 Flash TTS (Charon)...", file=sys.stderr)
    try:
        pcm_bytes = generate_gemini_tts(full_text, voice_name="Charon")
        raw_pcm_file = voice_path + ".raw"
        with open(raw_pcm_file, "wb") as pf:
            pf.write(pcm_bytes)

        subprocess.run([
            FFMPEG_PATH, "-y",
            "-f", "s16le", "-ar", "24000", "-ac", "1",
            "-i", raw_pcm_file,
            "-c:a", "libmp3lame", "-b:a", "192k",
            voice_path
        ], check=True, capture_output=True)

        try: os.remove(raw_pcm_file)
        except: pass

        from broll_manager import get_video_duration
        total_dur = get_video_duration(voice_path) or 20.0
        total_chars = max(1, sum(len(line[0]) for line in lines))
        curr_time = 0.1
        cues = []
        for line in lines:
            txt = line[0]
            fraction = len(txt) / total_chars
            dur = max(1.2, fraction * (total_dur - 0.4))
            cues.append((curr_time, curr_time + dur, txt))
            curr_time += dur

        print(f"[+] Studio-grade Gemini Charon male voice generated ({total_dur:.1f}s, {len(cues)} cues).", file=sys.stderr)
        return cues
    except Exception as e:
        print(f"[-] Gemini TTS failed: {e}", file=sys.stderr)
        raise RuntimeError(f"All natural human TTS engines failed: {e}")

def format_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{ms:02d}"

def chunk_text(text: str, start_sec: float, end_sec: float, style: str):
    words = text.strip().split()
    if not words:
        return []
    if len(words) <= 3:
        chunks = [words]
    elif len(words) == 4:
        chunks = [words[:2], words[2:]]
    elif len(words) == 5:
        chunks = [words[:3], words[3:]]
    elif len(words) == 6:
        chunks = [words[:3], words[3:]]
    else:
        chunks = []
        i = 0
        while i < len(words):
            take = 3 if (len(words) - i) >= 5 or (len(words) - i) == 3 else 2
            chunks.append(words[i:i+take])
            i += take

    total_chars = max(1, sum(sum(len(w) for w in ch) for ch in chunks))
    dur = max(0.5, end_sec - start_sec)
    res = []
    curr_t = start_sec
    for ch in chunks:
        ch_len = sum(len(w) for w in ch)
        ch_dur = (ch_len / total_chars) * dur
        res.append((curr_t, curr_t + ch_dur, ch, style))
        curr_t += ch_dur
    return res

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
Style: ViralMain,Arial Black,72,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,8,4,2,40,40,760,1
Style: HookBadge,Arial Black,34,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,3,0,1,6,3,2,40,40,1660,1
Style: HeaderBrand,Arial Black,36,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,3,0,1,6,3,2,40,40,1720,1
Style: HeaderSub,Arial Black,22,&H004422FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,5,2,2,40,40,1670,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    # Persistent channel branding headers (100% immune to FFmpeg drawtext font configuration crashes)
    dialogues.append("Dialogue: 0,0:00:00.00,0:01:00.00,HeaderBrand,,0,0,0,,ARISVEXX")
    dialogues.append("Dialogue: 0,0:00:00.00,0:01:00.00,HeaderSub,,0,0,0,,THE 48 LAWS OF POWER")
    # Badge for first 3.8s
    dialogues.append(f"Dialogue: 0,0:00:00.05,0:00:03.80,HookBadge,,0,0,0,,{badge}")

    # Map lines to cues
    total = min(len(lines), len(cues))
    for i in range(total):
        start_sec, end_sec, _ = cues[i]
        raw_text, style = lines[i]
        chunks = chunk_text(raw_text, start_sec, end_sec, style)
        for c_start, c_end, words, c_style in chunks:
            s_str = format_ass_time(c_start)
            e_str = format_ass_time(c_end)
            formatted_words = []
            for idx, w in enumerate(words):
                w_clean = w.upper().replace('"', '').replace("'", "")
                if idx == len(words) - 1:
                    if c_style == "Gold":
                        formatted_words.append(f"{{\\c&H0000FFFF&}}{w_clean}{{\\c&H00FFFFFF&}}")
                    elif c_style == "Red":
                        formatted_words.append(f"{{\\c&H002222FF&}}{w_clean}{{\\c&H00FFFFFF&}}")
                    else:
                        formatted_words.append(f"{{\\c&H00FFFF00&}}{w_clean}{{\\c&H00FFFFFF&}}")
                else:
                    formatted_words.append(w_clean)
            chunk_line_text = " ".join(formatted_words)
            dialogues.append(f"Dialogue: 0,{s_str},{e_str},ViralMain,,0,0,0,,{chunk_line_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues) + "\n")

def get_dark_phonk_track():
    candidates = [
        os.path.join(PROJECT_DIR, "data", "bgm", "dark_drift_phonk_1.mp3"),
        os.path.join(PROJECT_DIR, "data", "bgm", "shadow_force_phonk.mp3"),
        os.path.join(PROJECT_DIR, "data", "bgm", "aggressive_drift_phonk.mp3"),
    ]
    existing = [f for f in candidates if os.path.exists(f)]
    if existing:
        import random
        return random.choice(existing)
    return BGM_FILE

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
    selected_bgm = get_dark_phonk_track()
    print(f"[*] Selected Dark Phonk BGM: {os.path.basename(selected_bgm)}")

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.20:brightness=-0.03:saturation=0.90,"
        "vignette=PI/4.5,"
        "unsharp=3:3:0.9,"
        f"ass='{escaped_ass}'[v];"
        "[1:a]volume=1.35,bass=g=3:f=110[voice];"
        "[2:a]volume=0.22,bass=g=5:f=80[bgm];"
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
        "-i", selected_bgm,
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
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as ffe:
        print(f"[-] FFmpeg Render Error Output:\n{ffe.stderr}", file=sys.stderr, flush=True)
        raise RuntimeError(f"FFmpeg render failure: {ffe.stderr[-500:]}") from ffe
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

    # 10. Route to 'uploaded/' if live, otherwise 'not_uploaded/'
    try:
        import archive_uploaded_videos
        is_live_yt = pub_res.get("success") and not dry_run and pub_res.get("video_id") and not str(pub_res.get("video_id", "")).startswith("sim_")
        if is_live_yt:
            archive_uploaded_videos.save_to_uploaded_archive(
                video_path=output_video,
                title=title,
                description=desc,
                tags=["darkpsychology", "lawsofpower", "stoic", "mindset", "arisvexx", "sigmarules", "psychologyfacts", "shorts"],
                channel="ArisVexx",
                move=True,
                youtube_id=pub_res.get("video_id")
            )
        else:
            archive_uploaded_videos.save_to_not_uploaded(
                video_path=output_video,
                title=title,
                description=desc,
                tags=["darkpsychology", "lawsofpower", "stoic", "mindset", "arisvexx", "sigmarules", "psychologyfacts", "shorts"],
                channel="ArisVexx",
                move=True
            )
    except Exception as e:
        print(f"[-] Archive notice: {e}")

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
    try:
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
        print(json.dumps(res, indent=2), flush=True)
    except Exception as e:
        import traceback
        print(f"\n[CRITICAL PIPELINE EXCEPTION]: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)
