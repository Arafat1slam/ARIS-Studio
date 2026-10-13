"""
ARIS Instagram Reels Automation Publisher
Handles publishing 9:16 viral vertical reels directly to Instagram & connected Facebook Pages.
Uses saved persistent session to avoid repeated login challenges.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SESSION_FILE = os.path.join(PROJECT_DIR, "config", "instagram_session.json")
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

def get_instagram_client() -> "Client":
    from instagrapi import Client
    cl = Client()
    cl.delay_range = [1, 3]

    # 1. Load from session file on disk
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.get_timeline_feed()
            return cl
        except Exception as e:
            print(f"[!] Saved local session expired or invalid: {e}", file=sys.stderr)

    # 2. Load from environment variable (useful for GitHub Actions Secret)
    session_data = os.getenv("INSTAGRAM_SESSION_DATA")
    if session_data:
        try:
            settings_dict = json.loads(session_data)
            cl.set_settings(settings_dict)
            cl.get_timeline_feed()
            return cl
        except Exception as e:
            print(f"[!] Environment session data failed: {e}", file=sys.stderr)

    # 3. Fallback to username & password
    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    password = os.getenv("INSTAGRAM_PASSWORD", "").strip()
    if username and password:
        print(f"[*] Logging in to Instagram with credentials for @{username}...", file=sys.stderr)
        cl.login(username, password)
        try:
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            cl.dump_settings(SESSION_FILE)
        except Exception:
            pass
        return cl

    raise ValueError("No valid Instagram session or credentials found in environment or config.")

def publish_to_instagram(video_path: str, caption: str, share_to_facebook: bool = True, dry_run: bool = False) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if dry_run:
        print("[DRY-RUN] Simulating Instagram Reel upload...", file=sys.stderr)
        return {
            "success": True,
            "platform": "instagram",
            "media_id": f"sim_ig_{int(datetime.utcnow().timestamp())}",
            "code": "sim_reel_code",
            "url": "https://www.instagram.com/reel/sim_demo/",
            "caption": caption
        }

    try:
        cl = get_instagram_client()
        uname = cl.username or os.getenv("INSTAGRAM_USERNAME") or "rneitachi"
        thumb_path = f"{video_path}.jpg"
        if not os.path.exists(thumb_path):
            try:
                import shutil
                import subprocess
                ffmpeg_bin = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
                if not os.path.exists(ffmpeg_bin):
                    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
                subprocess.run(
                    [ffmpeg_bin, "-y", "-ss", "00:00:01", "-i", video_path, "-vframes", "1", "-q:v", "2", thumb_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
                )
            except Exception:
                pass

        thumb_arg = Path(thumb_path) if os.path.exists(thumb_path) else None

        # Upload Reel to Instagram
        print(f"[*] Uploading Reel ({os.path.getsize(video_path)/(1024*1024):.2f} MB)...", file=sys.stderr)
        try:
            if share_to_facebook:
                try:
                    media = cl.clip_upload(path=Path(video_path), caption=caption, thumbnail=thumb_arg, share_to_facebook=True)
                except Exception as fb_err:
                    print(f"[*] FB cross-post preflight skipped ({fb_err}). Uploading directly to Instagram...", file=sys.stderr)
                    media = cl.clip_upload(path=Path(video_path), caption=caption, thumbnail=thumb_arg, share_to_facebook=False)
            else:
                media = cl.clip_upload(path=Path(video_path), caption=caption, thumbnail=thumb_arg, share_to_facebook=False)
        finally:
            if thumb_path and os.path.exists(thumb_path):
                try: os.remove(thumb_path)
                except Exception: pass

        reel_url = f"https://www.instagram.com/reel/{media.code}/"
        print(f"[+] Successfully published to Instagram! Reel URL: {reel_url}", file=sys.stderr)

        # Post official website comment and pin it
        try:
            time.sleep(2)
            website_url = os.environ.get("WEBSITE_URL", "https://anime.ariswork.site")
            website_comment = (
                "🍿 Love watching Anime in Full HD?\n"
                f"Stream all episodes completely free on our official site: 👉 {website_url} 🔥"
            )
            comment_obj = cl.media_comment(media.id, website_comment)
            if comment_obj and getattr(comment_obj, "pk", None):
                try:
                    cl.comment_pin(media.id, comment_obj.pk)
                    print(f"[+] Pinned website comment on Instagram Reel ({comment_obj.pk})", file=sys.stderr)
                except Exception as pe:
                    print(f"[*] Comment posted, pin note: {pe}", file=sys.stderr)
        except Exception as ce:
            print(f"[!] Could not post/pin Instagram comment: {ce}", file=sys.stderr)
        return {
            "success": True,
            "platform": "instagram",
            "media_id": str(media.id),
            "code": media.code,
            "url": reel_url,
            "caption": caption
        }
    except Exception as e:
        print(f"[-] Instagram upload failed: {e}", file=sys.stderr)
        return {
            "success": False,
            "platform": "instagram",
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python instagram_publisher.py <video_path> [caption] [--dry-run]")
        sys.exit(1)

    v_path = sys.argv[1]
    v_cap = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "Viral Anime Edit #Shorts #Anime"
    is_dry = "--dry-run" in sys.argv
    res = publish_to_instagram(v_path, v_cap, dry_run=is_dry)
    print(json.dumps(res, indent=2))
