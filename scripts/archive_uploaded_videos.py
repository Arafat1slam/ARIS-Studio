import os
import sys
import json
import re
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOADED_DIR = os.path.join(PROJECT_DIR, "uploaded")
LEDGER_PATH = os.path.join(PROJECT_DIR, "config", "ledger.json")
FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

os.makedirs(UPLOADED_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    # Remove characters illegal in Windows filenames
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = clean.replace("#Shorts", "").replace("#shorts", "").strip()
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:60]

def save_to_uploaded_archive(video_path: str, title: str, description: str = "", tags: list = None, channel: str = "Itachi_Live", move: bool = False) -> str:
    """
    Archives an uploaded video into the 'uploaded/' folder with an accompanying
    info text file for easy manual uploading to Facebook Reels and TikTok.
    """
    os.makedirs(UPLOADED_DIR, exist_ok=True)
    channel_clean = "ArisVexx" if "arisvexx" in channel.lower() else "Itachi_Live"
    safe_title = sanitize_filename(title)
    base_name = f"[{channel_clean}] {safe_title}"
    target_mp4 = os.path.join(UPLOADED_DIR, f"{base_name}.mp4")
    target_txt = os.path.join(UPLOADED_DIR, f"{base_name}_info.txt")

    # If source exists, copy or move
    if os.path.exists(video_path):
        try:
            if move:
                shutil.move(video_path, target_mp4)
                print(f"[+] Moved published video to 'uploaded/': {os.path.basename(target_mp4)}", file=sys.stderr)
            else:
                shutil.copy2(video_path, target_mp4)
                print(f"[+] Copied published video to 'uploaded/': {os.path.basename(target_mp4)}", file=sys.stderr)
        except Exception as e:
            print(f"[-] Could not save video to archive: {e}", file=sys.stderr)

    # Format info text for manual copy-pasting to Facebook / TikTok
    tag_str = " ".join([f"#{t.strip('#')}" for t in (tags or ["shorts", "viral"])])
    caption_text = (
        f"=================================================================\n"
        f" CHANNEL: {channel_clean}\n"
        f" TITLE   : {title}\n"
        f"=================================================================\n\n"
        f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK ---\n\n"
        f"{description.strip() if description else title}\n\n"
        f"{tag_str}\n\n"
        f"=================================================================\n"
    )

    try:
        with open(target_txt, "w", encoding="utf-8") as f:
            f.write(caption_text)
        print(f"[+] Created caption file: {os.path.basename(target_txt)}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Could not write caption text: {e}", file=sys.stderr)

    return target_mp4

def sync_past_uploaded_videos():
    """
    Downloads any previously uploaded YouTube Shorts that were deleted locally,
    saving them into 'uploaded/' so they are always ready for Facebook & TikTok.
    """
    if not os.path.exists(LEDGER_PATH):
        print("[-] Ledger file not found.")
        return

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    records = ledger.get("records", [])
    print(f"[*] Found {len(records)} records in ledger. Checking 'uploaded/' directory...\n")

    synced_count = 0
    for r in records:
        yt_id = r.get("youtube_id")
        if not yt_id or yt_id.startswith("sim_"):
            continue

        raw_channel = r.get("channel", "Itachi_Live")
        channel = "ArisVexx" if "arisvexx" in raw_channel.lower() else "Itachi_Live"
        title = r.get("title", f"Video {yt_id}")
        safe_title = sanitize_filename(title)
        base_name = f"[{channel}] {safe_title}"
        target_mp4 = os.path.join(UPLOADED_DIR, f"{base_name}.mp4")
        target_txt = os.path.join(UPLOADED_DIR, f"{base_name}_info.txt")

        # 1. Download video if not already in uploaded/
        if not os.path.exists(target_mp4):
            print(f"[*] Downloading previous upload: {title} ({yt_id})...")
            cmd = [
                "yt-dlp",
                "--ffmpeg-location", FFMPEG_PATH,
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", target_mp4,
                f"https://www.youtube.com/shorts/{yt_id}"
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
                if os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 100000:
                    print(f"  [+] Saved video: {os.path.basename(target_mp4)}")
                    synced_count += 1
                else:
                    print(f"  [-] Failed to download {yt_id}: {res.stderr[:200]}")
            except Exception as e:
                print(f"  [-] Download error for {yt_id}: {e}")
        else:
            print(f"[=] Already in uploaded folder: {os.path.basename(target_mp4)}")

        # 2. Ensure caption text file exists
        if not os.path.exists(target_txt):
            desc = r.get("description", "")
            if not desc:
                if channel == "ArisVexx":
                    desc = f"{title}\n\nMaster the art of silent influence and power.\n\n#darkpsychology #stoic #lawsofpower #arisvexx #mindset"
                else:
                    desc = f"{title}\n\nWatch full HD episodes & updates: https://anime.ariswork.site\n\n#anime #otaku #animereels #viral"

            caption_text = (
                f"=================================================================\n"
                f" CHANNEL: {channel}\n"
                f" TITLE   : {title}\n"
                f" YOUTUBE : https://youtube.com/shorts/{yt_id}\n"
                f"=================================================================\n\n"
                f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK REELS & TIKTOK ---\n\n"
                f"{desc.strip()}\n\n"
                f"=================================================================\n"
            )
            with open(target_txt, "w", encoding="utf-8") as f:
                f.write(caption_text)
            print(f"  [+] Created info file: {os.path.basename(target_txt)}")

    print(f"\n[+] Sync complete! {synced_count} missing video(s) retrieved into '{UPLOADED_DIR}'.")

if __name__ == "__main__":
    sync_past_uploaded_videos()
