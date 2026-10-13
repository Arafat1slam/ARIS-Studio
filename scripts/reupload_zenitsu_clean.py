import os
import sys
import json
import hashlib
import shutil
from datetime import datetime, timezone

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

def reupload_clean_zenitsu():
    source_test_file = os.path.join(PROJECT_DIR, "data", "temp", "zenitsu_anti_copyright_test.mp4")
    uploaded_dir = os.path.join(PROJECT_DIR, "uploaded")
    os.makedirs(uploaded_dir, exist_ok=True)

    target_video_file = os.path.join(uploaded_dir, "[Itachi_Live] Zenitsu 60FPS God-Like Speed Remaster (V2 Copyright-Free).mp4")
    target_info_file = os.path.join(uploaded_dir, "[Itachi_Live] Zenitsu 60FPS God-Like Speed Remaster (V2 Copyright-Free)_info.txt")

    if not os.path.exists(source_test_file):
        print(f"[-] Source file not found: {source_test_file}")
        sys.exit(1)

    # Copy the freshly rendered anti-copyright video to final uploaded destination
    shutil.copy2(source_test_file, target_video_file)
    print(f"[+] Prepared final video: {target_video_file} ({os.path.getsize(target_video_file)/(1024*1024):.2f} MB)")

    title = "Zenitsu 60FPS God-Like Speed Remaster ⚡ #Shorts"
    desc = (
        "Zenitsu reaches God-like speed in this ultra-smooth 60FPS Demon Slayer Phonk edit! ⚡\n\n"
        "Remastered with dynamic 4K ambient spotlight framing, inverted lightning grading, and high-energy phonk audio.\n\n"
        "Watch your favorite anime in high quality at: https://anime.ariswork.site\n"
        "Subscribe to iταchι Live for daily viral anime fight scenes!\n\n"
        "#DemonSlayer #Zenitsu #KimetsuNoYaiba #AnimeEdits #AnimeShorts #60fps #Phonk #ItachiLive #Shorts"
    )
    tags = ["DemonSlayer", "Zenitsu", "KimetsuNoYaiba", "AnimeEdits", "AnimeShorts", "60fps", "Phonk", "ItachiLive", "Shorts"]

    print(f"[*] Uploading clean copyright-free version to Channel 1 (iταchι Live)...")
    res = youtube_meta_publisher.publish_to_youtube(
        video_path=target_video_file,
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
        video_url = f"https://www.youtube.com/shorts/{vid_id}"

        with open(target_video_file, "rb") as f:
            c_hash = hashlib.sha256(f.read()).hexdigest()

        now_str = datetime.now(timezone.utc).isoformat()
        record = {
            "content_hash": c_hash,
            "video_file": os.path.basename(target_video_file),
            "title": title,
            "channel": "Itachi_Live",
            "published_at": now_str,
            "youtube_id": vid_id,
            "status": "published",
            "timestamp": now_str
        }
        duplicate_checker.add_record(record)
        print(f"[+] Added clean record to ledger.json: ID {vid_id}")

        info_content = (
            f"=================================================================\n"
            f" CHANNEL: Itachi_Live\n"
            f" TITLE   : {title}\n"
            f" URL     : {video_url}\n"
            f" STATUS  : Copyright-Free Remaster (Phonk + Mirror + 1.08x Speed)\n"
            f"=================================================================\n\n"
            f"--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK ---\n\n"
            f"{desc}\n\n"
            f"=================================================================\n"
        )
        with open(target_info_file, "w", encoding="utf-8") as f:
            f.write(info_content)
        print(f"[+] Saved caption file: {target_info_file}")

        return {
            "success": True,
            "video_id": vid_id,
            "video_url": video_url,
            "uploaded_file": target_video_file
        }
    else:
        print(f"[-] Upload failed: {res}")
        return res

if __name__ == "__main__":
    reupload_clean_zenitsu()
