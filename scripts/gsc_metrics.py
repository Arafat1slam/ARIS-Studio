"""
Google Search Console SEO Metrics Puller for ARIS ANIME.
Pulls read-only impressions, clicks, CTR, and top ranking queries to inform content creation.
Saves metrics to data/logs/seo_metrics.json.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
LOG_DIR = os.path.join(PROJECT_DIR, "data", "logs")
OUTPUT_METRICS_FILE = os.path.join(LOG_DIR, "seo_metrics.json")

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

def refresh_google_token(client_id, client_secret, refresh_token):
    """Obtain a fresh OAuth2 access token using refresh_token."""
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as res:
        res_data = json.loads(res.read().decode("utf-8"))
        return res_data.get("access_token")

def pull_gsc_metrics(site_url=None, days_back=7, row_limit=25):
    """
    Fetch top query performance from Search Console API.
    """
    load_env()
    os.makedirs(LOG_DIR, exist_ok=True)

    site_url = site_url or os.environ.get("GSC_SITE_URL", "sc-domain:aris-anime.com")
    client_id = os.environ.get("GSC_CLIENT_ID") or os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("GSC_CLIENT_SECRET") or os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("GSC_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        # Graceful dry-run fallback if credentials are not yet linked
        demo_data = {
            "status": "pending_credentials",
            "message": "GSC credentials not yet set in .env. Returning baseline sample structure.",
            "site_url": site_url,
            "pulled_at": datetime.utcnow().isoformat() + "Z",
            "top_queries": [
                {"query": "watch anime online free hd", "clicks": 140, "impressions": 1820, "ctr": 0.0769, "position": 4.2},
                {"query": "aris anime streaming", "clicks": 95, "impressions": 410, "ctr": 0.2317, "position": 1.1},
                {"query": "jujutsu kaisen best fights", "clicks": 80, "impressions": 1200, "ctr": 0.0667, "position": 6.8}
            ]
        }
        with open(OUTPUT_METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(demo_data, f, indent=2)
        return demo_data

    try:
        access_token = refresh_google_token(client_id, client_secret, refresh_token)
        end_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=days_back + 2)).strftime("%Y-%m-%d")

        encoded_site = urllib.parse.quote(site_url, safe="")
        api_url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"

        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": row_limit
        }

        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("rows", [])
            formatted_queries = []
            for r in rows:
                formatted_queries.append({
                    "query": r.get("keys", [""])[0],
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "ctr": round(r.get("ctr", 0), 4),
                    "position": round(r.get("position", 0), 1)
                })

            result = {
                "status": "success",
                "site_url": site_url,
                "start_date": start_date,
                "end_date": end_date,
                "pulled_at": datetime.utcnow().isoformat() + "Z",
                "top_queries": formatted_queries
            }

            with open(OUTPUT_METRICS_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            return result

    except Exception as e:
        err = {"status": "error", "error": str(e), "pulled_at": datetime.utcnow().isoformat() + "Z"}
        with open(OUTPUT_METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(err, f, indent=2)
        return err

if __name__ == "__main__":
    res = pull_gsc_metrics()
    print(json.dumps(res, indent=2))
