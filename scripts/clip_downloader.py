"""
Viral Anime Clip Downloader using yt-dlp.
Finds and downloads trending, viral anime Shorts/Reels in maximum available quality.
Stores downloaded clips in data/approved_clips/ for processing.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(PROJECT_DIR, "config", "config.json")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "approved_clips")
DOWNLOAD_LOG = os.path.join(PROJECT_DIR, "data", "logs", "downloaded_sources.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_downloaded_sources():
    if os.path.exists(DOWNLOAD_LOG):
        try:
            with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_downloaded_source(info):
    sources = load_downloaded_sources()
    sources.append(info)
    os.makedirs(os.path.dirname(DOWNLOAD_LOG), exist_ok=True)
    with open(DOWNLOAD_LOG, "w", encoding="utf-8") as f:
        json.dump(sources, f, indent=2)

def download_clip(url_or_query, max_duration=60):
    """
    Download a single video or search and download the top viral result.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    already_downloaded = {s.get("id") for s in load_downloaded_sources()}

    # Output template: data/approved_clips/%(id)s.%(ext)s
    out_tmpl = os.path.join(OUTPUT_DIR, "%(title).50s_%(id)s.%(ext)s")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--max-filesize", "100M",
        "--match-filter", f"duration <= {max_duration} & !is_live",
        "--no-playlist",
        "--output", out_tmpl,
        "--print-json",
        "--no-warnings"
    ]

    if url_or_query.startswith("http://") or url_or_query.startswith("https://"):
        target = url_or_query
    else:
        # Search YouTube Shorts for query
        search_query = f"{url_or_query} shorts"
        target = f"ytsearch3:{search_query}"

    cmd.append(target)

    print(f"[*] Searching & downloading top viral anime clip for: '{url_or_query}'...", file=sys.stderr)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")

    if proc.returncode != 0 and not proc.stdout:
        print(f"[-] yt-dlp error: {proc.stderr}", file=sys.stderr)
        return {"success": False, "error": proc.stderr}

    downloaded = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            info = json.loads(line)
            video_id = info.get("id")
            if video_id in already_downloaded:
                continue

            file_path = info.get("_filename")
            if not file_path or not os.path.exists(file_path):
                # Fallback check
                title = info.get("title", "")
                ext = info.get("ext", "mp4")
                possible_path = os.path.join(OUTPUT_DIR, f"{title[:50]}_{video_id}.{ext}")
                if os.path.exists(possible_path):
                    file_path = possible_path

            record = {
                "id": video_id,
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "url": info.get("webpage_url"),
                "file_path": file_path,
                "downloaded_at": datetime.utcnow().isoformat() + "Z"
            }
            save_downloaded_source(record)
            downloaded.append(record)
            print(f"[+] Successfully downloaded: {info.get('title')} ({info.get('duration')}s)", file=sys.stderr)
            break # Get the best single viral clip
        except Exception as e:
            continue

    if not downloaded:
        return {"success": False, "message": "No new video found matching duration <= 60s or all candidates already downloaded."}

    return {"success": True, "clip": downloaded[0]}

def auto_fetch_viral_batch(count=3):
    """
    Fetch trending anime clips based on curated search queries.
    """
    config = load_config()
    default_queries = [
        "anime epic fight scene 4k",
        "jujutsu kaisen gojo epic moment 4k",
        "demon slayer tanjiro hinokami kagura 4k",
        "solo leveling sung jinwoo shadow monarch",
        "one piece luffy gear 5 viral edit",
        "bleach ichigo bankai 4k edit",
        "attack on titan levi vs beast titan 4k"
    ]
    queries = config.get("auto_sourcing", {}).get("search_queries", default_queries)

    results = []
    import random
    selected_queries = random.sample(queries, min(count, len(queries)))

    for q in selected_queries:
        res = download_clip(q)
        if res.get("success"):
            results.append(res["clip"])

    return {"fetched_count": len(results), "clips": results}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        res = download_clip(query)
    else:
        res = auto_fetch_viral_batch(count=1)
    print(json.dumps(res, indent=2))
