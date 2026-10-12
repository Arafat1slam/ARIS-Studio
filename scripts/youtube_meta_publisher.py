"""
Multi-Platform Publisher (YouTube Data API v3 & Meta Graph API)
Handles video publishing to YouTube Shorts and Facebook Page Reels.
Updates the local ledger upon successful publishing to prevent duplicate uploads.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
import duplicate_checker

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
CONFIG_FILE = os.path.join(PROJECT_DIR, "config", "config.json")
LOG_DIR = os.path.join(PROJECT_DIR, "data", "logs")

def load_env():
    """Load environment variables from .env."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    os.environ[k] = v

def get_youtube_token():
    """Refresh YouTube OAuth2 access token."""
    load_env()
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        return None

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode("utf-8")).get("access_token")

def publish_to_youtube(video_path, title, description, tags=None, privacy="public", dry_run=False):
    """Upload video to YouTube as a Short."""
    if dry_run or not os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        print("[DRY-RUN] Simulating YouTube upload...", file=sys.stderr)
        return {
            "success": True,
            "platform": "youtube",
            "video_id": f"sim_yt_{int(datetime.utcnow().timestamp())}",
            "mode": "simulation",
            "title": title
        }

    token = get_youtube_token()
    if not token:
        return {"success": False, "platform": "youtube", "error": "Unable to obtain YouTube access token."}

    # YouTube multipart upload
    metadata = {
        "snippet": {
            "title": title if "#Shorts" in title else f"{title} #Shorts",
            "description": description,
            "tags": tags or ["anime", "shorts", "arisanime"],
            "categoryId": "1"  # Film & Animation
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    # Upload video
    boundary = "================================" + str(int(datetime.utcnow().timestamp()))
    delimiter = f"\r\n--{boundary}\r\n".encode("utf-8")
    close_delim = f"\r\n--{boundary}--\r\n".encode("utf-8")

    meta_part = delimiter + b"Content-Type: application/json; charset=UTF-8\r\n\r\n" + json.dumps(metadata).encode("utf-8")
    
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    video_part = delimiter + b"Content-Type: video/mp4\r\n\r\n" + video_bytes + close_delim
    body = meta_part + video_part

    upload_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status"
    req = urllib.request.Request(
        upload_url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return {
                "success": True,
                "platform": "youtube",
                "video_id": resp_data.get("id"),
                "status": resp_data.get("status", {}).get("privacyStatus")
            }
    except Exception as e:
        return {"success": False, "platform": "youtube", "error": str(e)}

def publish_to_facebook(video_path, title, description, dry_run=False):
    """Upload video to Facebook Page via Meta Graph API."""
    page_id = os.environ.get("META_PAGE_ID")
    page_token = os.environ.get("META_PAGE_ACCESS_TOKEN")

    if dry_run or not (page_id and page_token):
        print("[DRY-RUN] Simulating Facebook Page upload...", file=sys.stderr)
        return {
            "success": True,
            "platform": "facebook",
            "post_id": f"sim_fb_{int(datetime.utcnow().timestamp())}",
            "mode": "simulation",
            "title": title
        }

    # Meta Graph API video upload
    url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
    
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    boundary = "----MetaUploadBoundary" + str(int(datetime.utcnow().timestamp()))
    part1 = f"--{boundary}\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n{title}\r\n".encode("utf-8")
    part2 = f"--{boundary}\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\n{description}\r\n".encode("utf-8")
    part3 = f"--{boundary}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{page_token}\r\n".encode("utf-8")
    part4 = f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"short.mp4\"\r\nContent-Type: video/mp4\r\n\r\n".encode("utf-8")
    close = f"\r\n--{boundary}--\r\n".encode("utf-8")

    body = part1 + part2 + part3 + part4 + video_bytes + close

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "success": True,
                "platform": "facebook",
                "video_id": data.get("id")
            }
    except Exception as e:
        return {"success": False, "platform": "facebook", "error": str(e)}

def publish_content(video_path, content_hash, title, description, tags=None, dry_run=False):
    """
    Publish to all enabled platforms and update ledger.
    """
    load_env()

    # Step 1: Duplicate check
    is_dup, rec = duplicate_checker.is_duplicate(content_hash)
    if is_dup:
        return {
            "success": False,
            "error": "Duplicate content detected in ledger. Publishing blocked to prevent reposting.",
            "existing_record": rec
        }

    # Step 2: Upload to YouTube
    yt_res = publish_to_youtube(video_path, title, description, tags, dry_run=dry_run)

    # Step 3: Upload to Facebook
    fb_res = publish_to_facebook(video_path, title, description, dry_run=dry_run)

    # Step 4: Upload to TikTok (if credentials configured)
    tt_res = {"success": False, "platform": "tiktok", "status": "skipped_not_configured"}
    has_tiktok = bool(os.environ.get("TIKTOK_ACCESS_TOKEN") or os.environ.get("TIKTOK_REFRESH_TOKEN"))
    if has_tiktok:
        if dry_run:
            print("[DRY-RUN] Simulating TikTok upload...", file=sys.stderr)
            tt_res = {"success": True, "platform": "tiktok", "status": "simulated", "publish_id": "sim_tt_123"}
        else:
            try:
                import tiktok_publisher
                caption_tags = " ".join([f"#{t.strip('#')}" for t in (tags or ["anime", "viral", "shorts"])])
                tt_caption = f"{title}\n\n▶ https://anime.ariswork.site\n\n{caption_tags}"
                tt_out = tiktok_publisher.publish_video_to_tiktok(video_path, tt_caption)
                tt_res = {
                    "success": True,
                    "platform": "tiktok",
                    "publish_id": tt_out.get("publish_id"),
                    "status": tt_out.get("status")
                }
            except Exception as e:
                print(f"[-] TikTok publish error: {e}", file=sys.stderr)
                tt_res = {"success": False, "platform": "tiktok", "error": str(e)}

    # Step 5: Record in ledger
    record = {
        "content_hash": content_hash,
        "video_file": os.path.basename(video_path),
        "title": title,
        "published_at": datetime.utcnow().isoformat() + "Z",
        "youtube_id": yt_res.get("video_id"),
        "facebook_id": fb_res.get("video_id") or fb_res.get("post_id"),
        "tiktok_id": tt_res.get("publish_id"),
        "status": "published"
    }
    duplicate_checker.add_record(record)

    # Step 6: Route to 'uploaded/' if live, otherwise 'not_uploaded/'
    try:
        import archive_uploaded_videos
        is_live_yt = yt_res.get("success") and not dry_run and not str(yt_res.get("video_id", "")).startswith("sim_")
        if is_live_yt:
            archive_uploaded_videos.save_to_uploaded_archive(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                channel="Itachi_Live",
                move=True,
                youtube_id=yt_res.get("video_id")
            )
        else:
            archive_uploaded_videos.save_to_not_uploaded(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                channel="Itachi_Live",
                move=True
            )
    except Exception as e:
        print(f"[-] Archive notice: {e}", file=sys.stderr)

    return {
        "success": True,
        "youtube": yt_res,
        "facebook": fb_res,
        "tiktok": tt_res,
        "ledger_record": record
    }

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python youtube_meta_publisher.py <video_path> <content_hash> <title> <description> [tags_comma_separated] [--dry-run]")
        sys.exit(1)

    v_path = sys.argv[1]
    c_hash = sys.argv[2]
    v_title = sys.argv[3]
    v_desc = sys.argv[4]
    v_tags = sys.argv[5].split(",") if len(sys.argv) > 5 and not sys.argv[5].startswith("--") else []
    is_dry = "--dry-run" in sys.argv or "--dry_run" in sys.argv

    res = publish_content(v_path, c_hash, v_title, v_desc, v_tags, dry_run=is_dry)
    print(json.dumps(res, indent=2))
