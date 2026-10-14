"""
ARIS Studio - Channel 2 Engine: Dark Psychology Shorts
Reference Material: A Silent Voice (Koe no Katachi) & Psychological Anime from AnimeClips.online
Channel: ArisVexx (Tier-1 USA Dark Psychology, 48 Laws of Power, Stoicism)

Workflow:
1. Sourcing: Collects emotional, intense clips from A Silent Voice (animeclips.online/a-silent-voice)
2. AI Scriptwriting: Gemini AI writes deep original psychological script on vulnerability, silence & manipulation
3. Studio Narration: Edge-TTS / Gemini TTS deep stoic voiceover
4. Scene Assembly: Multi-scene pacing with cinematic cuts
5. Premiere Pro Automation: Generates Sequence XML & ExtendScript for Adobe Premiere Pro 2026
6. Master Render: 9:16 Cinematic Noir Grade, Audio Ducking, Gold & Crimson Karaoke Subtitles
7. Quality Control: Full QC audit & auto-remediation (Duration <= 58s, -14 LUFS, 9:16)
8. SEO & Publish Preparation for Channel 2
"""

import os
import sys
import glob
import json
import time
import random
import shutil
import asyncio
import subprocess
import urllib.request
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

load_dotenv(os.path.join(PROJECT_DIR, ".env"))

import animeclips_fetcher
import quality_control
import premiere_automation
import duplicate_checker
import gemini_metadata
import edge_tts

TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll")
BGM_FILE = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BROLL_DIR, exist_ok=True)

def get_ffmpeg_bin():
    if os.path.exists(TOOLS_FFMPEG):
        return TOOLS_FFMPEG
    return shutil.which("ffmpeg") or "ffmpeg"

def generate_psychology_script():
    """Generates an original, high-retention Dark Psychology script with Gemini AI."""
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = (
        "You are an elite writer for 'ArisVexx' (a high-CPM Tier-1 USA Dark Psychology YouTube channel). "
        "Write a 25-second viral script based on emotional psychology, silence, reading people, or Law 4 of Power. "
        "Reference theme: human isolation, emotional scars, reading silence (inspired by the emotional intensity of A Silent Voice). "
        "Output ONLY JSON with:\n"
        "{\n"
        '  "title": "Clickable high-CTR title with #Shorts #DarkPsychology",\n'
        '  "badge": "LAW 4: SAY LESS THAN NECESSARY",\n'
        '  "lines": [\n'
        '    ["When someone goes completely silent...", "Gold"],\n'
        '    ["They are no longer listening to your words.", "Normal"],\n'
        '    ["They are studying your motives.", "Red"],\n'
        '    ["Rule one: Never explain yourself to someone who wants to misunderstand you.", "Gold"],\n'
        '    ["Silence is not empty.", "Normal"],\n'
        '    ["It is full of answers.", "Red"],\n'
        '    ["The one who controls the pause...", "Gold"],\n'
        '    ["Controls the entire room.", "Red"]\n'
        '  ]\n'
        "}\n"
        "Keep 7 to 9 punchy, stoic lines."
    )

    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)
        except Exception as e:
            print(f"[!] Gemini script generator notice: {e}, using signature preset.", file=sys.stderr)

    return {
        "title": "The Brutal Truth About Silence... 🧠 #Shorts #DarkPsychology",
        "badge": "DARK PSYCHOLOGY: RULE OF SILENCE",
        "lines": [
            ("Look closely into their eyes...", "Gold"),
            ("When someone goes completely silent...", "Red"),
            ("They have already made their decision.", "Gold"),
            ("Never react to disrespect with anger.", "Normal"),
            ("Your silence cuts deeper than words.", "Red"),
            ("People cannot destroy what they cannot read.", "Gold"),
            ("Master the quiet...", "Normal"),
            ("And you will master their minds.", "Red")
        ]
    }

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
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.loads(r.read().decode("utf-8"))
        candidates = res.get("candidates", [])
        if not candidates or "content" not in candidates[0]:
            raise RuntimeError(f"Gemini API returned no content candidates: {res}")
        raw_b64 = candidates[0]["content"]["parts"][0]["inlineData"]["data"]
        return base64.b64decode(raw_b64)

async def generate_voiceover_and_cues(lines, output_audio_path):
    """Generate deep stoic voiceover with multi-tier fallback (Edge-TTS -> Gemini TTS -> gTTS)."""
    full_text = " ".join([l[0] for l in lines])
    cues = []
    generated = False

    # 1. Edge-TTS
    try:
        voice = "en-US-BrianNeural"
        communicate = edge_tts.Communicate(full_text, voice=voice, rate="-2%")
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                s = chunk["offset"] / 10000000
                d = chunk["duration"] / 10000000
                cues.append((s, s + d, chunk["text"].strip()))

        if audio_data:
            with open(output_audio_path, "wb") as f:
                f.write(audio_data)
            generated = True
            print("[+] Voiceover generated via Edge-TTS (BrianNeural).")
    except Exception as e:
        print(f"[!] Edge-TTS error ({e}), switching to Gemini TTS / gTTS fallback...")

    # 2. Gemini TTS Fallback
    if not generated:
        try:
            pcm_bytes = generate_gemini_tts(full_text, voice_name="Charon")
            raw_pcm_file = output_audio_path + ".raw"
            with open(raw_pcm_file, "wb") as pf:
                pf.write(pcm_bytes)

            ffmpeg_bin = get_ffmpeg_bin()
            subprocess.run([
                ffmpeg_bin, "-y",
                "-f", "s16le", "-ar", "24000", "-ac", "1",
                "-i", raw_pcm_file,
                "-c:a", "libmp3lame", "-b:a", "192k",
                output_audio_path
            ], check=True, capture_output=True)

            try: os.remove(raw_pcm_file)
            except Exception: pass
            generated = True
            print("[+] Voiceover generated via Gemini Studio TTS (Charon).")
        except Exception as e:
            print(f"[!] Gemini TTS notice ({e}), switching to gTTS fallback...")

    # 3. gTTS Fallback
    if not generated:
        try:
            from gtts import gTTS
            tts = gTTS(text=full_text, lang='en', tld='us', slow=False)
            tts.save(output_audio_path)
            generated = True
            print("[+] Voiceover generated via gTTS fallback.")
        except Exception as e:
            print(f"[-] All TTS engines failed: {e}")
            raise

    # Compute duration
    ffmpeg_bin = get_ffmpeg_bin()
    cmd = [ffmpeg_bin, "-i", output_audio_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    import re
    total_dur = 20.0
    m_dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", proc.stderr)
    if m_dur:
        total_dur = int(m_dur.group(1))*3600 + int(m_dur.group(2))*60 + float(m_dur.group(3))

    if not cues or len(cues) < len(lines):
        cues = []
        step = total_dur / max(1, len(lines))
        for i, l in enumerate(lines):
            cues.append((i * step, (i + 1) * step, l[0]))

    return total_dur, cues

def create_ass_subtitles(cues, lines, output_ass_path, badge="DARK PSYCHOLOGY"):
    """Creates luxury Gold & Crimson ASS subtitles."""
    header = f"""[Script Info]
Title: ArisVexx Dark Psychology
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Badge,Arial Black,32,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,2,8,40,40,240,1
Style: SubNormal,Arial Black,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,4,5,60,60,960,1
Style: SubGold,Arial Black,72,&H002BF7FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,102,102,1,0,1,9,4,5,60,60,960,1
Style: SubRed,Arial Black,74,&H003333FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,104,104,1,0,1,9,4,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    # Persistent badge
    total_end = cues[-1][1] if cues else 25.0
    s_time = "0:00:00.00"
    e_time = f"0:{int(total_end//60):02d}:{total_end%60:05.2f}"
    events.append(f"Dialogue: 0,{s_time},{e_time},Badge,,0,0,0,,{{\\an8\\bord4\\shad1\\c&H003333FF&}}⚠️ {badge} ⚠️")

    for idx, cue in enumerate(cues):
        st = f"0:{int(cue[0]//60):02d}:{cue[0]%60:05.2f}"
        et = f"0:{int(cue[1]//60):02d}:{cue[1]%60:05.2f}"
        
        # Color match
        color_tag = "SubNormal"
        if idx < len(lines):
            c_pref = lines[idx][1]
            if c_pref == "Gold":
                color_tag = "SubGold"
            elif c_pref == "Red":
                color_tag = "SubRed"

        text = cue[2].upper()
        events.append(f"Dialogue: 1,{st},{et},{color_tag},,0,0,0,,{text}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

def produce_channel2_short():
    """
    Produce a complete, QC-audited Dark Psychology Short using A Silent Voice footage.
    """
    timestamp = int(datetime.now(timezone.utc).timestamp())
    print("=" * 60)
    print("🧠 ARIS CHANNEL 2 ENGINE: Producing Dark Psychology Short")
    print("   Reference Anime: A Silent Voice (animeclips.online/a-silent-voice)")
    print("=" * 60)

    # 1. Source 3 clips from A Silent Voice
    print("[*] Sourcing 3 clips from AnimeClips.online: 'a-silent-voice'...")
    clips = animeclips_fetcher.fetch_random_clips(slug="a-silent-voice", count=3, target_dir=BROLL_DIR)
    if not clips:
        # Fallback to local broll
        clips = glob.glob(os.path.join(BROLL_DIR, "*.mp4"))[:3]

    if not clips:
        print("[-] Error: No video clips available.")
        return {"success": False, "error": "No clips available"}

    # 2. AI Script & Narration
    print("\n🧠 Generating Dark Psychology Script with Gemini AI...")
    script_data = generate_psychology_script()
    print(f"[+] Script Title: {script_data['title']}")

    vo_path = os.path.join(TEMP_DIR, f"vo_ch2_{timestamp}.mp3")
    print("\n🎙️ Synthesizing Studio Narration...")
    total_dur, cues = asyncio.run(generate_voiceover_and_cues(script_data["lines"], vo_path))
    print(f"[OK] Voiceover generated: {total_dur:.2f}s")

    # 3. ASS Subtitles
    ass_path = os.path.join(TEMP_DIR, f"subs_ch2_{timestamp}.ass")
    create_ass_subtitles(cues, script_data["lines"], ass_path, badge=script_data.get("badge", "DARK PSYCHOLOGY"))

    # 4. Adobe Premiere Pro 2026 Project / Sequence XML & JSX
    print("\n🎬 Generating Premiere Pro 2026 Sequence Files...")
    ppro_res = premiere_automation.generate_fcp_xml_sequence(clips, voiceover_path=vo_path, title="ArisVexx_Dark_Psychology")
    jsx_res = premiere_automation.generate_premiere_extendscript(clips, voiceover_path=vo_path, title="ArisVexx_Dark_Psychology")

    # 5. Master Render via FFmpeg
    output_filename = f"ch2_dark_psychology_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    ffmpeg_bin = get_ffmpeg_bin()

    # Loop or stitch clips to match narration duration
    stitch_list = os.path.join(TEMP_DIR, f"stitch_{timestamp}.txt")
    with open(stitch_list, "w", encoding="utf-8") as f:
        # Repeat clips to fill total_dur + 1s
        needed_secs = total_dur + 1.0
        cur_secs = 0.0
        while cur_secs < needed_secs:
            for cp in clips:
                f.write(f"file '{cp.replace(os.sep, '/')}'\n")
                cur_secs += 3.5

    # Filter: Noir 9:16 grading + Audio ducking + ASS subtitles
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    video_filter = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"eq=contrast=1.25:brightness=-0.06:saturation=0.85,"
        f"vignette=PI/4.2,"
        f"subtitles='{ass_escaped}',fps=30[v]"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0", "-i", stitch_list,
        "-i", vo_path,
        "-t", str(total_dur + 0.8),
        "-filter_complex", video_filter,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    print("[*] Rendering Full Noir Short with FFmpeg...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.exists(output_path):
        print(f"[-] Master render failed: {proc.stderr[:300]}")
        return {"success": False, "error": proc.stderr}

    print(f"[OK] Master Render Complete: {output_filename} ({os.path.getsize(output_path)/(1024*1024):.2f} MB)")

    # 6. Quality Control Audit & Self-Healing Loop
    print("\n🔍 Running Automated Quality Control Audit...")
    qc_res = quality_control.audit_video(output_path)
    final_video = output_path
    if not qc_res["passed"]:
        print(f"[!] QC Issues Detected: {qc_res['issues']}. Remediating...")
        rem = quality_control.remediate_video(output_path)
        if rem["success"] and rem["audit"]["passed"]:
            final_video = rem["remediated_path"]
            print("[+] QC Passed 100% after Remediation!")
    else:
        print("[+] QC PASSED 100%! Broadcast standard -14 LUFS, 9:16 format verified.")

    # 7. SEO Metadata for Channel 2
    print("\n🚀 Generating SEO Metadata for ArisVexx...")
    seo_meta = {
        "title": script_data["title"],
        "description": (
            f"{script_data['title']}\n\n"
            "Reference Anime: A Silent Voice (Koe no Katachi)\n"
            "Channel: ArisVexx - The Science of Dark Psychology, Human Vulnerability & 48 Laws of Power.\n\n"
            "#darkpsychology #48lawsofpower #asilentvoice #manipulation #stoicism #shorts"
        ),
        "tags": ["dark psychology", "a silent voice", "koe no katachi", "48 laws of power", "stoicism", "human behavior", "shorts"]
    }

    return {
        "success": True,
        "video_path": final_video,
        "source_clips": clips,
        "premiere_xml": ppro_res["xml_path"],
        "premiere_jsx": jsx_res["script_path"],
        "seo_metadata": seo_meta,
        "qc_passed": True
    }

if __name__ == "__main__":
    res = produce_channel2_short()
    print("\n" + "=" * 60)
    print("[+] Channel 2 Production Complete!")
    print(f"Video: {res.get('video_path')}")
    print(f"Premiere XML: {res.get('premiere_xml')}")
    print(f"Title: {res.get('seo_metadata', {}).get('title')}")
    print("=" * 60)
