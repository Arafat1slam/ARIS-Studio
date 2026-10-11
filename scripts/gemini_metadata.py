"""
Gemini API Metadata Generator & Quota Tracker for ARIS Content Automation System.
Generates viral titles, SEO descriptions (with website link), tags, and logs usage.
Enforces non-negotiable free-tier guardrails.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
CONFIG_FILE = os.path.join(PROJECT_DIR, "config", "config.json")
LOG_DIR = os.path.join(PROJECT_DIR, "data", "logs")
QUOTA_FILE = os.path.join(LOG_DIR, "quota_tracker.json")

def load_env():
    """Load environment variables from .env file if present."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val

def load_config():
    """Load configuration parameters."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def track_quota(daily_limit=100):
    """
    Track daily API calls to prevent exceeding the free quota.
    Returns (allowed: bool, current_count: int).
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tracker = {}
    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                tracker = json.load(f)
        except Exception:
            tracker = {}

    current_count = tracker.get(today, 0)
    if current_count >= daily_limit:
        return False, current_count

    tracker[today] = current_count + 1
    with open(QUOTA_FILE, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2)

    return True, tracker[today]

def generate_metadata(clip_context="Epic Anime Moment", website_url=None):
    """
    Call Gemini API to generate title, description, tags, and SEO blurb.
    """
    load_env()
    config = load_config()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "GEMINI_API_KEY is not set in environment or .env file."
        }

    gemini_cfg = config.get("gemini", {})
    model = gemini_cfg.get("model", "gemini-2.5-flash")
    daily_limit = gemini_cfg.get("daily_request_limit", 100)

    # Check and update quota
    allowed, count = track_quota(daily_limit)
    if not allowed:
        return {
            "success": False,
            "error": f"Daily Gemini quota limit reached ({count}/{daily_limit}). Blocked to prevent paid billing."
        }

    site_url = website_url or os.environ.get("WEBSITE_URL") or config.get("pipeline", {}).get("website_url", "https://aris-anime.com")
    brand_name = os.environ.get("BRAND_NAME") or config.get("pipeline", {}).get("brand_name", "ARIS ANIME")

    prompt = f"""You are a professional social media manager and SEO specialist for an anime brand called "{brand_name}".
Create YouTube Shorts and Facebook Reels metadata for an anime clip described as: "{clip_context}".

Requirements:
1. Title: Catchy, engaging, under 90 characters, include 1-2 emojis and a popular anime hashtag (e.g. #Shorts).
2. Description:
   - 2-3 lines engaging anime hook or scene commentary.
   - Compulsory call to action (CTA): "Watch your favorite anime in high quality at: {site_url}"
   - 5-8 relevant viral anime hashtags including #{brand_name.replace(' ', '')} and #Anime.
3. Tags: An array of 10 relevant search keywords for YouTube.
4. Content Quality Score: A number from 1 to 10 evaluating virality.

Return ONLY a valid JSON object with the following keys:
{{
  "title": "string",
  "description": "string",
  "tags": ["tag1", "tag2"],
  "call_to_action_url": "{site_url}",
  "quality_score": 9
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            meta = json.loads(raw_text)
            meta["success"] = True
            meta["quota_used_today"] = count
            meta["model"] = model
            return meta
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if e.fp else str(e)
        return {"success": False, "error": f"Gemini API HTTP Error {e.code}: {err_msg}"}
    except Exception as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}

if __name__ == "__main__":
    context = sys.argv[1] if len(sys.argv) > 1 else "Goku Ultra Instinct vs Jiren epic battle scene"
    res = generate_metadata(clip_context=context)
    print(json.dumps(res, indent=2))
