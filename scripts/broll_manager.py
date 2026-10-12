import os
import sys
import json
import random
import subprocess
import re

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll")
HISTORY_FILE = os.path.join(PROJECT_DIR, "data", "logs", "broll_history.json")
FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

os.makedirs(BROLL_DIR, exist_ok=True)
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

BROLL_QUERIES = [
    "thomas shelby scene pack 4k vertical",
    "luxury car rainy night 4k vertical",
    "cillian murphy peaky blinders cold stare 4k",
    "christian bale american psycho dark luxury 4k",
    "marcus aurelius stoic statue dark aesthetic 4k",
    "batman gotham dark cinematic aesthetic 4k",
    "dark chess game slow motion cinematic 4k",
    "dark city rain street walking aesthetic 4k",
    "peaky blinders badass scene pack 4k",
    "dark aesthetic smoke silhouette 4k"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"used_videos": {}, "query_index": 0}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_video_duration(filepath):
    try:
        cmd = [FFMPEG_PATH, "-i", filepath]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            h, m_val, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + m_val * 60 + s
    except Exception as e:
        print(f"[!] Error reading duration for {filepath}: {e}", file=sys.stderr)
    return 30.0

def download_fresh_broll(query):
    print(f"[*] Searching & downloading fresh dark b-roll for: '{query}'...", file=sys.stderr)
    try:
        search_cmd = [
            "yt-dlp",
            f"ytsearch5:{query}",
            "--dump-json",
            "--flat-playlist"
        ]
        res = subprocess.run(search_cmd, capture_output=True, text=True, errors="ignore")
        candidates = []
        for line in res.stdout.strip().split("\n"):
            if line:
                try:
                    d = json.loads(line)
                    vid_id = d.get("id")
                    dur = d.get("duration", 0)
                    if vid_id and dur and 10 <= dur <= 600:
                        candidates.append((vid_id, d.get("title", "broll")))
                except Exception:
                    pass

        if not candidates:
            print("[-] No candidate b-roll found online.", file=sys.stderr)
            return None

        # Pick first candidate
        vid_id, title = candidates[0]
        out_path = os.path.join(BROLL_DIR, f"broll_{vid_id}.mp4")
        if os.path.exists(out_path):
            return out_path

        dl_cmd = [
            "yt-dlp",
            "--ffmpeg-location", FFMPEG_PATH,
            "-f", "bestvideo[height<=1080]/best[height<=1080]",
            "-o", out_path,
            "--force-overwrites",
            f"https://www.youtube.com/watch?v={vid_id}"
        ]
        dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, errors="ignore")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100000:
            print(f"[+] Downloaded fresh b-roll: {title[:40]} ({os.path.basename(out_path)})", file=sys.stderr)
            return out_path
    except Exception as e:
        print(f"[-] Error downloading fresh b-roll: {e}", file=sys.stderr)
    return None

def get_unique_broll(segment_duration=28):
    """
    Returns (video_filepath, start_offset_seconds)
    Ensures that no two videos use the same background visual or same timestamp!
    """
    history = load_history()
    used_videos = history.get("used_videos", {})

    # 1. Check local files in BROLL_DIR
    local_files = [
        os.path.join(BROLL_DIR, f) for f in os.listdir(BROLL_DIR)
        if f.endswith((".mp4", ".webm", ".mkv")) and os.path.getsize(os.path.join(BROLL_DIR, f)) > 100000
    ]

    # Also check if shelby_full exists in temp
    temp_shelby = os.path.join(PROJECT_DIR, "data", "temp", "shelby_full.mp4")
    if os.path.exists(temp_shelby) and temp_shelby not in local_files:
        local_files.append(temp_shelby)

    # Shuffle to vary usage
    random.shuffle(local_files)

    for fpath in local_files:
        base_name = os.path.basename(fpath)
        dur = get_video_duration(fpath)
        used_offsets = used_videos.get(base_name, [])

        # Candidate offsets spaced every segment_duration seconds
        candidate_offsets = []
        offset = 0
        while offset + segment_duration <= dur:
            if offset not in used_offsets:
                candidate_offsets.append(offset)
            offset += int(segment_duration + 2)

        if candidate_offsets:
            chosen_offset = candidate_offsets[0]
            if base_name not in used_videos:
                used_videos[base_name] = []
            used_videos[base_name].append(chosen_offset)
            history["used_videos"] = used_videos
            save_history(history)
            print(f"[*] Selected unique b-roll: {base_name} at offset {chosen_offset}s (Duration: {dur:.1f}s)", file=sys.stderr)
            return fpath, chosen_offset

    # 2. If all local clips/segments are exhausted, download a fresh one!
    query_idx = history.get("query_index", 0) % len(BROLL_QUERIES)
    chosen_query = BROLL_QUERIES[query_idx]
    history["query_index"] = (query_idx + 1) % len(BROLL_QUERIES)

    fresh_file = download_fresh_broll(chosen_query)
    if fresh_file and os.path.exists(fresh_file):
        base_name = os.path.basename(fresh_file)
        if base_name not in used_videos:
            used_videos[base_name] = []
        used_videos[base_name].append(0)
        history["used_videos"] = used_videos
        save_history(history)
        print(f"[*] Selected freshly downloaded b-roll: {base_name} at offset 0s", file=sys.stderr)
        return fresh_file, 0

    # Fallback to whatever is available
    if local_files:
        fallback = local_files[0]
        rand_off = random.randint(0, max(0, int(get_video_duration(fallback) - segment_duration)))
        return fallback, rand_off

    raise RuntimeError("No b-roll clips available and could not download fresh b-roll.")

if __name__ == "__main__":
    b_path, b_off = get_unique_broll(28)
    print(f"B-Roll: {b_path} | Offset: {b_off}s")
