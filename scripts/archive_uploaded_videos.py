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
NOT_UPLOADED_DIR = os.path.join(PROJECT_DIR, "not_uploaded")
LEDGER_PATH = os.path.join(PROJECT_DIR, "config", "ledger.json")
FFMPEG_PATH = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

os.makedirs(UPLOADED_DIR, exist_ok=True)
os.makedirs(NOT_UPLOADED_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = clean.replace("#Shorts", "").replace("#shorts", "").strip()
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:60]

def build_caption_text(channel: str, title: str, description: str, tags: list = None, youtube_id: str = None) -> str:
    tag_str = " ".join([f"#{t.strip('#')}" for t in (tags or ["shorts", "viral"])])
    yt_line = f" YOUTUBE : https://youtube.com/shorts/{youtube_id}\n" if youtube_id else ""
    return (
        f"=================================================================\n"
        f" CHANNEL: {channel}\n"
        f" TITLE   : {title}\n"
        f"{yt_line}"
        f"=================================================================\n\n"
        f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK ---\n\n"
        f"{description.strip() if description else title}\n\n"
        f"{tag_str}\n\n"
        f"=================================================================\n"
    )

def save_to_not_uploaded(video_path: str, title: str, description: str = "", tags: list = None, channel: str = "Itachi_Live", move: bool = False) -> str:
    """
    Saves a newly generated video into 'not_uploaded/' pending user review or scheduled upload.
    """
    os.makedirs(NOT_UPLOADED_DIR, exist_ok=True)
    channel_clean = "ArisVexx" if "arisvexx" in channel.lower() else "Itachi_Live"
    safe_title = sanitize_filename(title)
    base_name = f"[{channel_clean}] {safe_title}"
    target_mp4 = os.path.join(NOT_UPLOADED_DIR, f"{base_name}.mp4")
    target_txt = os.path.join(NOT_UPLOADED_DIR, f"{base_name}_info.txt")

    if os.path.exists(video_path):
        try:
            if move:
                shutil.move(video_path, target_mp4)
            else:
                shutil.copy2(video_path, target_mp4)
            print(f"[+] Saved pending video to 'not_uploaded/': {os.path.basename(target_mp4)}", file=sys.stderr)
        except Exception as e:
            print(f"[-] Could not save to not_uploaded: {e}", file=sys.stderr)

    caption_text = build_caption_text(channel_clean, title, description, tags)
    try:
        with open(target_txt, "w", encoding="utf-8") as f:
            f.write(caption_text)
        print(f"[+] Created caption file: {os.path.basename(target_txt)}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Could not write caption file: {e}", file=sys.stderr)

    return target_mp4

def promote_to_uploaded(title: str, channel: str = "Itachi_Live", youtube_id: str = None) -> bool:
    """
    Moves a video and its info.txt from 'not_uploaded/' to 'uploaded/' once successfully published!
    """
    channel_clean = "ArisVexx" if "arisvexx" in channel.lower() else "Itachi_Live"
    safe_title = sanitize_filename(title)
    base_name = f"[{channel_clean}] {safe_title}"
    
    src_mp4 = os.path.join(NOT_UPLOADED_DIR, f"{base_name}.mp4")
    src_txt = os.path.join(NOT_UPLOADED_DIR, f"{base_name}_info.txt")
    dst_mp4 = os.path.join(UPLOADED_DIR, f"{base_name}.mp4")
    dst_txt = os.path.join(UPLOADED_DIR, f"{base_name}_info.txt")

    moved = False
    if os.path.exists(src_mp4):
        try:
            shutil.move(src_mp4, dst_mp4)
            moved = True
            print(f"[+] Promoted video from 'not_uploaded/' to 'uploaded/': {os.path.basename(dst_mp4)}", file=sys.stderr)
        except Exception as e:
            print(f"[-] Error promoting mp4 to uploaded: {e}", file=sys.stderr)

    if os.path.exists(src_txt):
        try:
            # Update info file with YouTube ID if available
            with open(src_txt, "r", encoding="utf-8") as f:
                content = f.read()
            if youtube_id and "YOUTUBE :" not in content:
                content = content.replace("=================================================================\n\n---", f" YOUTUBE : https://youtube.com/shorts/{youtube_id}\n=================================================================\n\n---")
            with open(dst_txt, "w", encoding="utf-8") as f:
                f.write(content)
            os.remove(src_txt)
        except Exception as e:
            try:
                shutil.move(src_txt, dst_txt)
            except Exception:
                pass

    return moved

def save_to_uploaded_archive(video_path: str, title: str, description: str = "", tags: list = None, channel: str = "Itachi_Live", move: bool = True, youtube_id: str = None) -> str:
    """
    Called when a video has been SUCCESSFULLY uploaded to YouTube.
    Moves it to 'uploaded/' folder.
    """
    os.makedirs(UPLOADED_DIR, exist_ok=True)
    channel_clean = "ArisVexx" if "arisvexx" in channel.lower() else "Itachi_Live"
    safe_title = sanitize_filename(title)
    base_name = f"[{channel_clean}] {safe_title}"
    target_mp4 = os.path.join(UPLOADED_DIR, f"{base_name}.mp4")
    target_txt = os.path.join(UPLOADED_DIR, f"{base_name}_info.txt")

    # If already in not_uploaded, promote it
    not_up_mp4 = os.path.join(NOT_UPLOADED_DIR, f"{base_name}.mp4")
    if os.path.exists(not_up_mp4):
        promote_to_uploaded(title, channel=channel_clean, youtube_id=youtube_id)
        return target_mp4

    if os.path.exists(video_path):
        try:
            if move:
                shutil.move(video_path, target_mp4)
                print(f"[+] Moved published video to 'uploaded/': {os.path.basename(target_mp4)}", file=sys.stderr)
            else:
                shutil.copy2(video_path, target_mp4)
                print(f"[+] Copied published video to 'uploaded/': {os.path.basename(target_mp4)}", file=sys.stderr)
        except Exception as e:
            print(f"[-] Could not save video to uploaded archive: {e}", file=sys.stderr)

    caption_text = build_caption_text(channel_clean, title, description, tags, youtube_id=youtube_id)
    try:
        with open(target_txt, "w", encoding="utf-8") as f:
            f.write(caption_text)
        print(f"[+] Created caption file in uploaded/: {os.path.basename(target_txt)}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Could not write caption text: {e}", file=sys.stderr)

    return target_mp4

def sync_past_uploaded_videos():
    """
    Downloads previously uploaded YouTube Shorts that were deleted locally,
    ONLY when explicitly requested by user.
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

        if not os.path.exists(target_mp4):
            print(f"[*] Downloading previous upload: {title} ({yt_id})...")
            cmd = [
                sys.executable, "-m", "yt_dlp",
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
            except Exception as e:
                print(f"  [-] Download error for {yt_id}: {e}")
        else:
            print(f"[=] Already in uploaded folder: {os.path.basename(target_mp4)}")

    print(f"\n[+] Sync complete! {synced_count} missing video(s) retrieved into '{UPLOADED_DIR}'.")

if __name__ == "__main__":
    sync_past_uploaded_videos()
