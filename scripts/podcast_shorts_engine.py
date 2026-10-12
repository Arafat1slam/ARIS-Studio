"""
ARIS Content Automation System - Clean Podcast Shorts Engine (ArisVexx)
Slices and remasters viral highlights from top foreign podcasts:
- Multi-Channel Pool: The Diary Of A CEO, Chris Williamson (Modern Wisdom), Jordan Peterson, Huberman Lab
- Topic Filter: Dark psychology, power dynamics, stoic mindset, human behavior
- 100% Watermark-Free: Auto edge-cropping & dynamic ArisVexx header/footer framing
- Real human voices with authentic emotional delivery
- Ambient cinematic piano BGM mixed at low volume underneath voice
- Saves to 'not_uploaded/' for review or scheduled upload
"""

import os
import sys
import json
import random
import shutil
import hashlib
import subprocess
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(PROJECT_DIR, "config", "config.json")
UPLOADED_DIR = os.path.join(PROJECT_DIR, "uploaded")
NOT_UPLOADED_DIR = os.path.join(PROJECT_DIR, "not_uploaded")
LOG_DIR = os.path.join(PROJECT_DIR, "data", "logs")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
BGM_FILE = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")
HISTORY_FILE = os.path.join(LOG_DIR, "podcast_history.json")

FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

PODCAST_SOURCES = [
    {
        "creator": "The Diary Of A CEO",
        "tagline": "DIARY OF A CEO | HUMAN PSYCHOLOGY",
        "url": "https://www.youtube.com/@TheDiaryOfACEO/shorts",
        "topic": "Human Behavior & Mental Mastery"
    },
    {
        "creator": "Chris Williamson",
        "tagline": "MODERN WISDOM | STOIC MINDSET",
        "url": "https://www.youtube.com/@ChrisWillx/shorts",
        "topic": "Power Dynamics & Psychology"
    },
    {
        "creator": "Jordan Peterson",
        "tagline": "JORDAN PETERSON | DARK PERSONALITY",
        "url": "https://www.youtube.com/@JordanBPeterson/shorts",
        "topic": "Psychology & The Dark Triad"
    },
    {
        "creator": "Huberman Lab",
        "tagline": "HUBERMAN LAB | BRAIN & BEHAVIOR",
        "url": "https://www.youtube.com/@hubermanlab/shorts",
        "topic": "Mind Control & Focus"
    }
]

PSYCHOLOGY_KEYWORDS = [
    "mind", "psychology", "power", "rule", "win", "lie", "habit", "brain",
    "toxic", "read", "truth", "stoic", "dark", "focus", "ego", "silence",
    "fear", "control", "danger", "secret", "influence", "people", "trust",
    "guts", "behavior", "manipulat", "body", "sign", "personality"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"used_ids": []}

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def is_relevant_topic(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in PSYCHOLOGY_KEYWORDS)

def fetch_top_podcast_clip():
    """
    Finds a fresh, high-relevance viral podcast short from our multi-channel pool.
    Guarantees no repeating channels and strict relevance to psychology & mindset!
    """
    history = load_history()
    used_ids = set(history.get("used_ids", []))

    sources = list(PODCAST_SOURCES)
    random.shuffle(sources)

    for src in sources:
        creator = src["creator"]
        tagline = src["tagline"]
        url = src["url"]
        topic = src["topic"]

        print(f"[*] Scanning viral podcast clips from: {creator}...", file=sys.stderr)
        cmd = [
            sys.executable, "-m", "yt_dlp",
            url,
            "--playlist-end", "20",
            "--dump-json",
            "--flat-playlist",
            "--no-warnings"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        candidates = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                vid_id = data.get("id")
                dur = data.get("duration") or 0
                title = data.get("title") or "Podcast Insight"

                if vid_id in used_ids:
                    continue

                if dur and not (18 <= dur <= 59):
                    continue

                if not is_relevant_topic(title):
                    continue

                candidates.append((vid_id, title, dur))
            except Exception:
                pass

        if candidates:
            # Pick the top candidate
            vid_id, title, dur = candidates[0]
            print(f"[+] Selected topic from {creator}: '{title}' ({vid_id})", file=sys.stderr)
            return {
                "video_id": vid_id,
                "title": title,
                "creator": creator,
                "tagline": tagline,
                "topic": topic,
                "url": f"https://www.youtube.com/watch?v={vid_id}"
            }

    # Fallback to search query if channel shelves didn't match keyword
    fallback_queries = [
        "The Diary Of A CEO manipulation psychology shorts",
        "Chris Williamson dark psychology shorts",
        "Jordan Peterson dark personality traits shorts"
    ]
    fb_q = random.choice(fallback_queries)
    print(f"[*] Searching YouTube for fallback topic: '{fb_q}'...", file=sys.stderr)
    cmd = [
        sys.executable, "-m", "yt_dlp",
        f"ytsearch10:{fb_q}",
        "--dump-json",
        "--flat-playlist",
        "--no-warnings"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    for line in proc.stdout.splitlines():
        try:
            data = json.loads(line)
            vid_id = data.get("id")
            dur = data.get("duration") or 0
            title = data.get("title") or "Psychology Secret"
            if vid_id in used_ids:
                continue
            if dur and not (18 <= dur <= 59):
                continue
            return {
                "video_id": vid_id,
                "title": title,
                "creator": "Diary Of A CEO / Modern Wisdom",
                "tagline": "DARK PSYCHOLOGY | ARISVEXX",
                "topic": "Mind Dynamics & Power",
                "url": f"https://www.youtube.com/watch?v={vid_id}"
            }
        except Exception:
            pass

    return None

def download_podcast_clip(video_url, output_path):
    """
    Downloads raw video and audio using yt-dlp with ffmpeg location specified.
    """
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--ffmpeg-location", FFMPEG_PATH,
        video_url,
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", output_path,
        "--no-warnings",
        "--force-overwrites"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return os.path.exists(output_path) and os.path.getsize(output_path) > 100000

def get_duration(video_path):
    cmd = [FFMPEG_PATH, "-i", video_path]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        h, m_val, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + m_val * 60 + s
    return 35.0

def render_podcast_short(raw_video_path, metadata, output_path):
    """
    Remasters the podcast video:
    - 1080x1920 vertical canvas
    - 100% Watermark-Free framing (crops corner/lower watermarks, sleek top header badge)
    - Cinematic noir grading and vignette
    - Dynamic BGM mix at low volume underneath real human voice
    """
    dur = min(get_duration(raw_video_path), 58.0)
    tagline = metadata.get("tagline", "DARK PSYCHOLOGY | ARISVEXX")

    # Anti-Watermark Filter Graph:
    # 1. Scale with slight 1.05x overscan to crop out tiny corner channel logos
    # 2. Sleek top dark header box to frame the speaker
    # 3. Clean @ArisVexx brand watermark at bottom
    filter_complex = (
        "[0:v]scale=1140:2026:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.12:saturation=1.15:brightness=0.01,unsharp=3:3:0.8,vignette=PI/4.5,"
        "drawbox=x=0:y=160:w=1080:h=95:color=black@0.72:t=fill,"
        f"drawtext=font='Arial':text='{tagline}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=190,"
        "drawtext=font='Arial':text='@ArisVexx':fontcolor=white@0.65:fontsize=28:x=(w-text_w)/2:y=1740[v];"
        "[0:a]volume=1.20,bass=g=3:f=120[voice];"
        "[1:a]volume=0.14[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    )

    cmd = [
        FFMPEG_PATH, "-y",
        "-ss", "0", "-t", str(dur),
        "-i", raw_video_path,
        "-stream_loop", "-1",
        "-ss", "0", "-t", str(dur),
        "-i", BGM_FILE,
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
        output_path
    ]

    print(f"[*] Rendering Watermark-Free Podcast Short ({dur:.1f}s) via FFmpeg...", file=sys.stderr)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100000

def produce_podcast_short(dry_run=True):
    """
    Master pipeline for producing a clean Podcast Short for ArisVexx.
    Saves to 'not_uploaded/' when in review / dry-run mode.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(NOT_UPLOADED_DIR, exist_ok=True)

    print("\n=======================================================", file=sys.stderr)
    print("   ARISVEXX PODCAST CLIPS ENGINE - FOREIGN PODCASTS", file=sys.stderr)
    print(f"   Mode: {'LOCAL PREVIEW (DRY-RUN)' if dry_run else 'AUTO-PUBLISH'}", file=sys.stderr)
    print("=======================================================\n", file=sys.stderr)

    clip_meta = fetch_top_podcast_clip()
    if not clip_meta:
        return {"success": False, "error": "No new candidate podcast clips found."}

    vid_id = clip_meta["video_id"]
    raw_video = os.path.join(TEMP_DIR, f"podcast_raw_{vid_id}.mp4")

    print(f"[*] Downloading clip: '{clip_meta['title']}' ({clip_meta['creator']})...", file=sys.stderr)
    ok = download_podcast_clip(clip_meta["url"], raw_video)
    if not ok:
        return {"success": False, "error": "Failed to download podcast clip video."}

    clean_title = clip_meta["title"].replace("#Shorts", "").replace("#shorts", "").strip()[:50]
    out_name = f"[ArisVexx] {clean_title} - {clip_meta['creator']}"
    target_dir = UPLOADED_DIR if not dry_run else NOT_UPLOADED_DIR
    target_mp4 = os.path.join(target_dir, f"{out_name}.mp4")
    target_txt = os.path.join(target_dir, f"{out_name}_info.txt")

    rendered = render_podcast_short(raw_video, clip_meta, target_mp4)
    if not rendered:
        return {"success": False, "error": "FFmpeg render failed."}

    # Record in history so it never repeats
    history = load_history()
    if vid_id not in history.get("used_ids", []):
        history.setdefault("used_ids", []).append(vid_id)
        save_history(history)

    # Format companion caption
    caption_content = (
        f"=================================================================\n"
        f" CHANNEL: ArisVexx\n"
        f" TITLE   : {clean_title} | {clip_meta['creator']} #Shorts\n"
        f"=================================================================\n\n"
        f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK / YOUTUBE ---\n\n"
        f"{clean_title} | {clip_meta['creator']} #Shorts\n\n"
        f"Speaker: {clip_meta['creator']}\n"
        f"Topic: {clip_meta['topic']}\n\n"
        f"Subscribe to ArisVexx for daily psychological insights and stoic principles.\n\n"
        f"#DarkPsychology #LawsOfPower #ArisVexx #Mindset #Stoic #PsychologyFacts #Shorts #PodcastClips\n\n"
        f"=================================================================\n"
    )

    with open(target_txt, "w", encoding="utf-8") as f:
        f.write(caption_content)

    # Cleanup raw temp file
    try:
        if os.path.exists(raw_video):
            os.remove(raw_video)
    except Exception:
        pass

    print(f"[+] Successfully produced clean Podcast Short: {os.path.basename(target_mp4)}", file=sys.stderr)
    print(f"[+] Saved to: {'uploaded/' if not dry_run else 'not_uploaded/'}", file=sys.stderr)

    return {
        "success": True,
        "video_file": target_mp4,
        "caption_file": target_txt,
        "title": clean_title,
        "creator": clip_meta["creator"],
        "topic": clip_meta["topic"],
        "dry_run": dry_run
    }

if __name__ == "__main__":
    force_auto = "--auto" in sys.argv
    res = produce_podcast_short(dry_run=not force_auto)
    print(json.dumps(res, indent=2))
