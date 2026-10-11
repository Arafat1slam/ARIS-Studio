import os
import sys
import time
import json
import requests
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(ENV_PATH)

CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')
CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET')

def get_valid_access_token() -> str:
    access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    refresh_token = os.getenv('TIKTOK_REFRESH_TOKEN')

    if not refresh_token and not access_token:
        raise ValueError("Missing TikTok credentials. Run 'python scripts/auth_tiktok.py' first.")

    # Always test or refresh token
    if refresh_token:
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        payload = {
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        try:
            resp = requests.post(token_url, data=payload, headers=headers, timeout=15)
            data = resp.json()
            if resp.status_code == 200 and 'access_token' in data:
                new_access = data['access_token']
                new_refresh = data.get('refresh_token', refresh_token)
                set_key(ENV_PATH, "TIKTOK_ACCESS_TOKEN", new_access)
                if 'refresh_token' in data:
                    set_key(ENV_PATH, "TIKTOK_REFRESH_TOKEN", new_refresh)
                print("[*] TikTok access token refreshed successfully.")
                return new_access
        except Exception as e:
            print(f"[!] Warning: Token refresh attempt had an error: {e}. Falling back to existing access token.")

    return access_token

def query_creator_privacy(access_token: str) -> str:
    """Queries allowed privacy levels for creator account."""
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    try:
        resp = requests.post(url, headers=headers, json={}, timeout=15)
        data = resp.json()
        if data.get('error', {}).get('code') == 'ok':
            creator_data = data.get('data', {})
            allowed_levels = creator_data.get('privacy_level_options', [])
            print(f"[*] TikTok creator allowed privacy options: {allowed_levels}")
            if "PUBLIC_TO_EVERYONE" in allowed_levels:
                return "PUBLIC_TO_EVERYONE"
            elif "MUTUAL_FOLLOW_FRIENDS" in allowed_levels:
                return "MUTUAL_FOLLOW_FRIENDS"
            elif "SELF_ONLY" in allowed_levels:
                return "SELF_ONLY"
    except Exception as e:
        print(f"[!] Warning querying creator info: {e}")
    return "PUBLIC_TO_EVERYONE"

def publish_video_to_tiktok(video_path: str, caption: str) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    access_token = get_valid_access_token()
    file_size = os.path.getsize(video_path)

    # TikTok title limit is roughly 2200 chars or 150 chars depending on endpoint. Keeping it punchy.
    if len(caption) > 1500:
        caption = caption[:1490] + "..."

    privacy_level = query_creator_privacy(access_token)
    print(f"[*] Initializing TikTok video upload (Size: {file_size / (1024*1024):.2f} MB, Privacy: {privacy_level})...")

    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    init_payload = {
        "post_info": {
            "title": caption,
            "privacy_level": privacy_level,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }

    resp = requests.post(init_url, headers=headers, json=init_payload, timeout=30)
    data = resp.json()

    if data.get('error', {}).get('code') != 'ok':
        err_msg = data.get('error', {}).get('message', 'Unknown error')
        raise RuntimeError(f"TikTok Init Upload Failed: {err_msg} (Response: {data})")

    publish_id = data['data']['publish_id']
    upload_url = data['data']['upload_url']
    print(f"[+] Upload initialized. Publish ID: {publish_id}")

    # Transfer video file chunk via PUT
    print("[*] Uploading video binary data to TikTok CDN...")
    upload_headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
    }

    with open(video_path, 'rb') as f:
        video_bytes = f.read()

    put_resp = requests.put(upload_url, data=video_bytes, headers=upload_headers, timeout=120)
    if put_resp.status_code not in (200, 201):
        raise RuntimeError(f"TikTok Video Chunk Upload Failed with status {put_resp.status_code}: {put_resp.text}")

    print("[+] Video bytes successfully uploaded to TikTok CDN!")

    # Check status
    status_url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
    status_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    status_payload = {"publish_id": publish_id}

    print("[*] Checking TikTok publishing processing status...")
    status_result = "PROCESSING_UPLOAD"
    for attempt in range(1, 6):
        time.sleep(3)
        s_resp = requests.post(status_url, headers=status_headers, json=status_payload, timeout=20)
        s_data = s_resp.json()
        if s_data.get('error', {}).get('code') == 'ok':
            status_result = s_data.get('data', {}).get('status', 'PROCESSING_UPLOAD')
            print(f"[*] Attempt {attempt}: TikTok Status = {status_result}")
            if status_result in ('PUBLISH_COMPLETE', 'SUCCESS'):
                break

    return {
        "publish_id": publish_id,
        "status": status_result,
        "caption": caption,
        "privacy_level": privacy_level
    }

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_video = sys.argv[1]
        cap = sys.argv[2] if len(sys.argv) > 2 else "Epic Anime Short! #anime #viral"
        res = publish_video_to_tiktok(test_video, cap)
        print(f"[RESULT] {json.dumps(res, indent=2)}")
    else:
        print("Usage: python scripts/tiktok_publisher.py <video_path> [caption]")
