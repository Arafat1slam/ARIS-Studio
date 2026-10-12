import sys
import os
import json
import hashlib
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import publish_channel2
import duplicate_checker

def upload():
    video_path = os.path.join(PROJECT_DIR, "uploaded", "[ArisVexx] Unlock Your Dark Power.mp4")
    if not os.path.exists(video_path):
        print(f"Error: File not found at {video_path}")
        sys.exit(1)

    title = "Unlock Your Dark Power #Shorts"
    desc = (
        "Unlock your dark power and command respect in silence.\n\n"
        "Welcome to ArisVexx. We decode human psychology, power dynamics, and stoic principles.\n\n"
        "#darkpsychology #lawsofpower #stoic #mindset #arisvexx #sigmarules #psychologyfacts #shorts"
    )
    tags = [
        "darkpsychology", "lawsofpower", "stoic", "mindset",
        "arisvexx", "sigmarules", "psychologyfacts", "shorts"
    ]

    print(f"[*] Starting upload for: {video_path}")
    res = publish_channel2.publish_to_channel2(
        video_path=video_path,
        title=title,
        description=desc,
        tags=tags,
        privacy="public",
        dry_run=False
    )

    print("Upload Response:")
    print(json.dumps(res, indent=2))

    if res.get("success"):
        vid_id = res.get("video_id")
        video_url = res.get("video_url")
        with open(video_path, "rb") as f:
            c_hash = hashlib.sha256(f.read()).hexdigest()

        # Update ledger
        now_str = datetime.utcnow().isoformat() + "Z"
        record = {
            "content_hash": c_hash,
            "video_file": os.path.basename(video_path),
            "title": title,
            "channel": "ArisVexx",
            "published_at": now_str,
            "youtube_id": vid_id,
            "status": "published"
        }
        duplicate_checker.add_record(record)
        print(f"[+] Updated ledger record with real YouTube ID: {vid_id}")

        # Update caption file with URL
        txt_path = os.path.join(PROJECT_DIR, "uploaded", "[ArisVexx] Unlock Your Dark Power_info.txt")
        info_content = (
            "=================================================================\n"
            f" CHANNEL: ArisVexx\n"
            f" TITLE   : {title}\n"
            f" URL     : {video_url}\n"
            "=================================================================\n\n"
            "--- COPY-PASTE THIS CAPTION FOR FACEBOOK / TIKTOK ---\n\n"
            "Unlock your dark power and command respect in silence.\n\n"
            "#darkpsychology #stoic #mindset #arisvexx #shorts\n\n"
            "=================================================================\n"
        )
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(info_content)
        print(f"[+] Updated caption info file: {txt_path}")
        return res
    else:
        print("[-] Upload failed!")
        return res

if __name__ == "__main__":
    upload()
