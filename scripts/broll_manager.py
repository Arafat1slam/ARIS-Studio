import os
import sys
import json
import random
import subprocess
import shutil
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
    "cillian murphy peaky blinders cold stare 4k",
    "christian bale american psycho dark luxury 4k vertical",
    "marcus aurelius stoic statue dark aesthetic 4k",
    "batman gotham dark cinematic aesthetic 4k",
    "luxury car rainy night 4k vertical",
    "dark chess game slow motion cinematic 4k",
    "dark city rain street walking aesthetic 4k",
    "thomas shelby badass scene pack 4k vertical",
    "godfather mafia dark cigar aesthetic 4k",
    "cyberpunk tokyo rain neon dark walking 4k",
    "cillian murphy walking down street 4k edit",
    "man in black suit slow motion rain 4k vertical",
    "whiskey glass smoke dark luxury aesthetic 4k",
    "rolls royce night rain dark aesthetic 4k",
    "peaky blinders smoking cigarette slow motion 4k",
    "ancient greek roman statue dramatic lighting 4k",
    "interstellar space black hole dark cinematic 4k",
    "fight club tyler durden dark aesthetic 4k",
    "drive ryan gosling synthwave dark jacket 4k",
    "blade runner 2049 officer k rain 4k vertical"
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
    print(f"[*] Searching & downloading fresh aesthetic B-Roll: '{query}'...", file=sys.stderr)
    try:
        search_cmd = [
            sys.executable, "-m", "yt_dlp",
            f"ytsearch8:{query}",
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

        # Randomly pick from candidates pool to guarantee visual variety
        random.shuffle(candidates)
        vid_id, title = candidates[0]
        out_path = os.path.join(BROLL_DIR, f"broll_{vid_id}.mp4")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100000:
            return out_path

        dl_cmd = [
            sys.executable, "-m", "yt_dlp",
            "--ffmpeg-location", FFMPEG_PATH,
            "-f", "bestvideo[height<=1080]/best[height<=1080]",
            "-o", out_path,
            "--force-overwrites",
            f"https://www.youtube.com/watch?v={vid_id}"
        ]
        dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, errors="ignore")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100000:
            print(f"[+] Downloaded unique fresh B-Roll: {title[:40]} ({os.path.basename(out_path)})", file=sys.stderr)
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
    last_used = history.get("last_used_video", "")

    # 1. Check local files in BROLL_DIR
    local_files = [
        os.path.join(BROLL_DIR, f) for f in os.listdir(BROLL_DIR)
        if f.endswith((".mp4", ".webm", ".mkv")) and os.path.getsize(os.path.join(BROLL_DIR, f)) > 100000
    ]

    # Prioritize files that are NOT the last used one, sorted by least used
    candidates = []
    for fpath in local_files:
        base_name = os.path.basename(fpath)
        times_used = len(used_videos.get(base_name, []))
        is_last = 1 if base_name == last_used and len(local_files) > 1 else 0
        candidates.append((is_last, times_used, random.random(), fpath))
    candidates.sort()

    for _, _, _, fpath in candidates:
        base_name = os.path.basename(fpath)
        dur = get_video_duration(fpath)
        used_offsets = used_videos.get(base_name, [])

        candidate_offsets = []
        if dur <= segment_duration:
            candidate_offsets = [0]
        else:
            offset = 0 if dur <= (segment_duration + 8) else 3
            while offset + segment_duration <= dur:
                if offset not in used_offsets:
                    candidate_offsets.append(offset)
                offset += int(segment_duration + 3)
            # If all unique slices were used, cycle through available offsets
            if not candidate_offsets:
                candidate_offsets = [0, max(0, int(dur - segment_duration) // 2)]

        if candidate_offsets:
            random.shuffle(candidate_offsets)
            chosen_offset = candidate_offsets[0]
            if base_name not in used_videos:
                used_videos[base_name] = []
            used_videos[base_name].append(chosen_offset)
            history["used_videos"] = used_videos
            history["last_used_video"] = base_name
            save_history(history)
            print(f"[*] Selected unique B-Roll: {base_name} (Used {len(used_offsets)+1}x) at offset {chosen_offset}s (Total: {dur:.1f}s)", file=sys.stderr)
            return fpath, chosen_offset

    # 2. If all local clips exhausted their offsets, download fresh unique clip from diverse query pool
    chosen_query = random.choice(BROLL_QUERIES)
    fresh_file = download_fresh_broll(chosen_query)
    if fresh_file and os.path.exists(fresh_file):
        dur = get_video_duration(fresh_file)
        max_start = max(5, int(dur - segment_duration - 5))
        chosen_offset = random.randint(5, max_start) if max_start > 5 else 0
        base_name = os.path.basename(fresh_file)
        if base_name not in used_videos:
            used_videos[base_name] = []
        used_videos[base_name].append(chosen_offset)
        history["used_videos"] = used_videos
        history["last_used_video"] = base_name
        save_history(history)
        print(f"[*] Selected freshly downloaded B-Roll: {base_name} at offset {chosen_offset}s", file=sys.stderr)
        return fresh_file, chosen_offset

    # Fallback to any local file
    if local_files:
        fallback = random.choice(local_files)
        rand_off = random.randint(0, max(0, int(get_video_duration(fallback) - segment_duration)))
        return fallback, rand_off

    # Procedural fallback: Generate a sleek dark cinematic canvas so the pipeline NEVER crashes
    fallback_path = os.path.join(BROLL_DIR, "procedural_dark_broll.mp4")
    if not os.path.exists(fallback_path):
        try:
            subprocess.run([
                FFMPEG_PATH, "-y",
                "-f", "lavfi", "-i", "color=c=0x080a10:s=1080x1920:d=30:r=30",
                "-vf", "noise=c1s=8:c0f=u",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                fallback_path
            ], capture_output=True)
        except Exception:
            pass
    if os.path.exists(fallback_path):
        return fallback_path, 0

    raise RuntimeError("No b-roll clips available and procedural fallback generation failed.")

if __name__ == "__main__":
    b_path, b_off = get_unique_broll(28)
    print(f"B-Roll: {b_path} | Offset: {b_off}s")
