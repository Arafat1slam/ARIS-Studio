"""
Direct Publisher for Channel 1: iταchι Live.
Uploads the approved Zenitsu Godspeed Short to YouTube.
On success:
- Updates ledger.json to track published hash
- Moves video & info.txt from 'not_uploaded/' to 'uploaded/'
- Appends live YouTube URL to info.txt
"""

import os
import sys
import json
import hashlib
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import youtube_meta_publisher
import duplicate_checker
import shutil

def upload_zenitsu():
    not_uploaded_dir = os.path.join(PROJECT_DIR, "not_uploaded")
    uploaded_dir = os.path.join(PROJECT_DIR, "uploaded")
    os.makedirs(uploaded_dir, exist_ok=True)

    # Locate Zenitsu video and caption
    mp4_file = None
    txt_file = None
    for f in os.listdir(not_uploaded_dir):
        if "Zenitsu" in f and f.endswith(".mp4"):
            mp4_file = os.path.join(not_uploaded_dir, f)
        elif "Zenitsu" in f and f.endswith(".txt"):
            txt_file = os.path.join(not_uploaded_dir, f)

    if not mp4_file or not os.path.exists(mp4_file):
        print(f"[-] Zenitsu video not found in {not_uploaded_dir}")
        return {"success": False, "error": "Video file not found"}

    title = "Zenitsu's GODSPEED is INSANE! ⚡ Demon Slayer Power-Up! #Shorts"
    desc = (
        "Witness Zenitsu unleash his terrifying Godspeed! ⚡ The speed and power are absolutely breathtaking in this iconic Demon Slayer moment.\n\n"
        "Watch your favorite anime in high quality at: https://anime.ariswork.site\n\n"
        "#DemonSlayer #Zenitsu #KimetsuNoYaiba #AnimeEdits #AnimeShorts #Shorts"
    )
    tags = ["DemonSlayer", "Zenitsu", "KimetsuNoYaiba", "AnimeEdits", "AnimeShorts", "Shorts"]

    print(f"[*] Uploading Channel 1 Short: {os.path.basename(mp4_file)}...")
    print(f"[*] Title: {title}")

    res = youtube_meta_publisher.publish_to_youtube(
        video_path=mp4_file,
        title=title,
        description=desc,
        tags=tags,
        privacy="public",
        dry_run=False
    )

    print("\nYouTube Upload Response:")
    print(json.dumps(res, indent=2))

    if res.get("success") and res.get("video_id") and not str(res.get("video_id")).startswith("sim_"):
        vid_id = res.get("video_id")
        video_url = f"https://youtube.com/shorts/{vid_id}"

        with open(mp4_file, "rb") as f:
            c_hash = hashlib.sha256(f.read()).hexdigest()

        # 1. Update ledger
        now_str = datetime.now().isoformat() + "Z"
        record = {
            "content_hash": c_hash,
            "video_file": os.path.basename(mp4_file),
            "title": title,
            "channel": "Itachi_Live",
            "published_at": now_str,
            "youtube_id": vid_id,
            "status": "published",
            "timestamp": now_str
        }
        duplicate_checker.add_record(record)
        print(f"[+] Added record to ledger.json: ID {vid_id}")

        # 2. Move files from not_uploaded/ to uploaded/
        dst_mp4 = os.path.join(uploaded_dir, os.path.basename(mp4_file))
        dst_txt = os.path.join(uploaded_dir, os.path.basename(txt_file)) if txt_file else None

        shutil.move(mp4_file, dst_mp4)
        if txt_file and os.path.exists(txt_file):
            shutil.move(txt_file, dst_txt)
            # Update info file with live URL
            info_content = (
                f"=================================================================\n"
                f" CHANNEL: Itachi_Live\n"
                f" TITLE   : {title}\n"
                f" URL     : {video_url}\n"
                f"=================================================================\n\n"
                f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK ---\n\n"
                f"{desc}\n\n"
                f"=================================================================\n"
            )
            with open(dst_txt, "w", encoding="utf-8") as f:
                f.write(info_content)

        print(f"[+] Video successfully moved to uploaded/: {os.path.basename(dst_mp4)}")
        print(f"[+] Live YouTube URL: {video_url}")

        return {
            "success": True,
            "video_id": vid_id,
            "video_url": video_url,
            "uploaded_file": dst_mp4
        }
    else:
        print(f"[-] Upload failed or returned simulated ID: {res}")
        return res

if __name__ == "__main__":
    out = upload_zenitsu()
    print(json.dumps(out, indent=2))
