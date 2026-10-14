"""
ARIS Studio - Scenepacks.com Automation Engine
Direct integration with https://scenepacks.com/ for high quality Movie & Anime Scenepacks.
"""

import os
import re
import time
import json
import urllib.request
import urllib.parse
import subprocess

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "scenepacks_cache.json")
CLIPS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "broll", "scenepacks")
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

FFMPEG_BIN = r"tools\ffmpeg.exe" if os.path.exists(r"tools\ffmpeg.exe") else "ffmpeg"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Known popular scenepack IDs on scenepacks.com:
POPULAR_PACKS = {
    # Dark Psychology / Movies:
    "fight_club_1080p": 1161,
    "fight_club_tyler": 3552,
    "peaky_blinders_tommy": 3495,
    # Anime / Sakuga:
    "gojo_s2": 1297,
    "sukuna_s2": 3227,
    "toji_s2": 3477
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Failed to save scenepack cache: {e}")

def get_scenepack_stream_url(download_id):
    """
    Resolves the signed Cloudflare R2 / S3 download stream URL for a given scenepack download ID.
    Handles CSRF, gate token, and sponsor countdown.
    """
    cache = load_cache()
    cached = cache.get(str(download_id))
    now = time.time()
    
    if cached and cached.get("expires_at", 0) > now + 300:
        return cached.get("stream_url")
        
    url = f"https://scenepacks.com/download/{download_id}"
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    try:
        resp = opener.open(req)
        html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[-] Error opening scenepacks.com/download/{download_id}: {e}")
        return None
        
    config_match = re.search(r'\{\s*"gateToken":\s*"([^"]+)",\s*"recordCsrfToken":\s*"([^"]+)",\s*"recordUrl":\s*"([^"]+)"', html)
    if not config_match:
        print(f"[-] Could not find gate config for download {download_id}")
        return None
        
    gate_token = config_match.group(1)
    csrf_token = config_match.group(2)
    record_url = config_match.group(3)
    
    post_url = "https://scenepacks.com" + record_url
    payload = json.dumps({
        "source": "direct",
        "gate_token": gate_token,
        "referrer": ""
    }).encode("utf-8")
    
    post_req = urllib.request.Request(post_url, data=payload, headers={
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
        "Referer": url,
        "Origin": "https://scenepacks.com"
    })
    
    stream_url = None
    try:
        post_resp = opener.open(post_req)
        res_data = json.loads(post_resp.read().decode("utf-8"))
        stream_url = res_data.get("redirectUrl")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_body)
            if err_json.get("code") == "download_gate_required":
                wait_sec = err_json.get("retry_after", 27)
                print(f"[*] scenepacks.com download gate active: waiting {wait_sec}s for download ID {download_id}...")
                time.sleep(wait_sec + 2)
                
                # Retry POST
                post_resp2 = opener.open(post_req)
                res_data2 = json.loads(post_resp2.read().decode("utf-8"))
                stream_url = res_data2.get("redirectUrl")
        except Exception as ex:
            print(f"[-] Scenepack gate resolution error: {ex}")
            return None
            
    if stream_url:
        print(f"[+] Successfully resolved scenepack {download_id} stream URL!")
        cache[str(download_id)] = {
            "stream_url": stream_url,
            "expires_at": now + 20000 # 5.5 hours validity
        }
        save_cache(cache)
        return stream_url
    else:
        print(f"[-] Failed to obtain stream URL for {download_id}")
        return None

def extract_scenes_from_stream(stream_url, cuts, output_prefix="scene"):
    """
    Rapidly extracts multiple scenes using FFmpeg range streaming.
    cuts: list of (start_sec, duration_sec)
    Returns: list of local clip paths
    """
    extracted_clips = []
    for idx, (ss, dur) in enumerate(cuts):
        out_filename = f"{output_prefix}_{idx:02d}_{int(ss)}s_{int(dur)}s.mp4"
        out_path = os.path.join(CLIPS_DIR, out_filename)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 500000:
            print(f"[OK] Using cached clip: {out_filename} ({os.path.getsize(out_path)/(1024*1024):.2f} MB)")
            extracted_clips.append(out_path)
            continue
            
        print(f"[*] Extracting shot {idx+1}/{len(cuts)} at {ss}s ({dur}s)...")
        # Format ss as HH:MM:SS
        hours = int(ss // 3600)
        minutes = int((ss % 3600) // 60)
        seconds = ss % 60
        ss_str = f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"
        
        cmd = [
            FFMPEG_BIN, "-y",
            "-ss", ss_str,
            "-i", stream_url,
            "-t", str(dur),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            out_path
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0 and os.path.exists(out_path):
            print(f"[+] Extracted: {out_filename} ({os.path.getsize(out_path)/(1024*1024):.2f} MB)")
            extracted_clips.append(out_path)
        else:
            print(f"[-] Extraction failed for {ss_str}: {proc.stderr[-200:]}")
            
    return extracted_clips

if __name__ == "__main__":
    # Test resolving Fight Club and Gojo
    url_fc = get_scenepack_stream_url(1161)
    print("Fight Club Stream:", url_fc[:80] if url_fc else "None")
