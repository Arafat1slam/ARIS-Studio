"""
One-Time YouTube OAuth 2.0 Authorization Flow for Desktop Client.
Opens browser, captures authorization code on local server,
exchanges for refresh_token, and saves directly to .env.
"""

import os
import sys
import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
SECRET_FILE = os.path.join(PROJECT_DIR, "client_secret_2_1027563140587-9prsproq2gim6u03hvkm862md0crhnh9.apps.googleusercontent.com.json")

AUTH_CODE = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if "code" in params:
            AUTH_CODE = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
            <html>
            <body style="font-family: Arial; text-align: center; padding-top: 50px; background: #0f172a; color: #f8fafc;">
                <h1 style="color: #22c55e;">&#10004; Authorization Successful!</h1>
                <p>Your YouTube Channel is now connected to ARIS Content Automation.</p>
                <p>You can close this tab and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed or code not found.")

    def log_message(self, format, *args):
        # Silence HTTP server logs
        return

def get_client_credentials():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            inst = data.get("installed") or data.get("web", {})
            return inst.get("client_id"), inst.get("client_secret")
    return None, None

def update_env(key_values):
    lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    keys_updated = set()
    new_lines = []
    for line in lines:
        updated = False
        for k, v in key_values.items():
            if line.startswith(f"{k}="):
                new_lines.append(f"{k}={v}\n")
                keys_updated.add(k)
                updated = True
                break
        if not updated:
            new_lines.append(line)

    for k, v in key_values.items():
        if k not in keys_updated:
            new_lines.append(f"{k}={v}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def run_auth():
    client_id, client_secret = get_client_credentials()
    if not client_id or not client_secret:
        print("[-] Client secret file not found or invalid.", file=sys.stderr)
        return False

    port = 8080
    redirect_uri = f"http://localhost:{port}"

    # Step 1: Save Client ID & Secret to .env
    update_env({
        "YOUTUBE_CLIENT_ID": client_id,
        "YOUTUBE_CLIENT_SECRET": client_secret
    })
    print("[+] Saved YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET to .env")

    # Step 2: Build Auth URL
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly"
    ]
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    print("\n" + "="*70)
    print("  CONNECT YOUR YOUTUBE CHANNEL")
    print("="*70)
    print("Opening your browser to authorize access...")
    print(f"\nIf browser doesn't open automatically, copy-paste this URL:\n\n{auth_url}\n")
    print("="*70)

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    # Start local server on port 8080
    server_address = ("localhost", port)
    httpd = HTTPServer(server_address, OAuthHandler)
    print(f"[*] Waiting for authorization on {redirect_uri} ...")

    while AUTH_CODE is None:
        httpd.handle_request()

    httpd.server_close()
    print("[+] Authorization code received!")

    # Step 3: Exchange code for refresh token
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            refresh_token = data.get("refresh_token")
            access_token = data.get("access_token")

            if refresh_token:
                update_env({"YOUTUBE_REFRESH_TOKEN": refresh_token})
                print("[+] SUCCESS! Refresh token captured and saved to .env!")
                print(f"[+] Access Token obtained: {access_token[:15]}...")
                return True
            else:
                print("[-] Warning: Refresh token not in response. If previously authorized, delete token and try with prompt=consent.")
                return False
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8") if e.fp else str(e)
        print(f"[-] Token exchange error: {err}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = run_auth()
    sys.exit(0 if success else 1)
