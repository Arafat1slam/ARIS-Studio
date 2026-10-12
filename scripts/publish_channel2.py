import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH, override=True)

def get_channel2_access_token():
    load_dotenv(ENV_PATH, override=True)
    cid = (os.getenv("YOUTUBE_CLIENT_ID_2") or os.getenv("YOUTUBE_CLIENT_ID") or "").strip("'\"")
    csec = (os.getenv("YOUTUBE_CLIENT_SECRET_2") or os.getenv("YOUTUBE_CLIENT_SECRET") or "").strip("'\"")
    rtok = (os.getenv("YOUTUBE_REFRESH_TOKEN_2") or "").strip("'\"")
    if not (cid and csec and rtok):
        raise ValueError("Missing Channel 2 credentials in .env")

    data = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": csec,
        "refresh_token": rtok,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode("utf-8")).get("access_token")

def publish_to_channel2(video_path: str, title: str, description: str, tags: list = None, privacy: str = "public", dry_run: bool = False) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if dry_run:
        print("[DRY-RUN] Simulating ArisVexx upload...", file=sys.stderr)
        return {
            "success": True,
            "channel": "ArisVexx",
            "video_id": f"sim_arisvexx_{int(datetime.utcnow().timestamp())}",
            "title": title
        }

    token = get_channel2_access_token()
    if not token:
        return {"success": False, "channel": "ArisVexx", "error": "Failed to obtain access token"}

    full_title = title if "#Shorts" in title else f"{title} #Shorts"
    metadata = {
        "snippet": {
            "title": full_title[:100],
            "description": description,
            "tags": tags or ["darkpsychology", "stoicism", "mindset", "shorts", "arisvexx", "lawsofpower"],
            "categoryId": "27"  # Education / Philosophy
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

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
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )

    print(f"[*] Uploading video to ArisVexx channel ({len(body) / (1024*1024):.2f} MB)...", file=sys.stderr)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            vid_id = data.get("id")
            print(f"[+] Successfully uploaded to ArisVexx! Video ID: {vid_id}", file=sys.stderr)
            return {
                "success": True,
                "channel": "ArisVexx",
                "channel_id": CHANNEL_ID_2,
                "video_id": vid_id,
                "video_url": f"https://www.youtube.com/shorts/{vid_id}",
                "title": title
            }
    except Exception as e:
        print(f"[-] ArisVexx upload failed: {e}", file=sys.stderr)
        return {"success": False, "channel": "ArisVexx", "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish_channel2.py <video_path> <title> [description]")
        sys.exit(1)
    v_path = sys.argv[1]
    v_title = sys.argv[2]
    v_desc = sys.argv[3] if len(sys.argv) > 3 else "Dark Psychology & Laws of Power | ArisVexx\n\n#DarkPsychology #Shorts"
    res = publish_to_channel2(v_path, v_title, v_desc)
    print(json.dumps(res, indent=2))
