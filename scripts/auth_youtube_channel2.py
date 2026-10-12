import os
import sys
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID_2") or os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET_2") or os.getenv("YOUTUBE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"
PORT = 8080

auth_code_holder = {}

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code_holder["code"] = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family:sans-serif; text-align:center; padding-top:60px; background:#0f0c29; color:#fff;">
                <h1 style="color:#00e5ff;">ArisVexx (Channel 2) Connected!</h1>
                <p style="font-size:18px;">Tokens saved to .env. You can close this tab and return to terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif "error" in query:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization Error</h1>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def exchange_code_for_tokens(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    resp = requests.post(token_url, data=payload)
    if resp.status_code != 200:
        print(f"[-] Token exchange error: {resp.text}")
        return False
    
    tokens = resp.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    if not refresh_token:
        print("[!] Warning: No refresh token returned. Re-running with prompt=consent is recommended.")
        
    # Get Channel details
    ch_url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&mine=true"
    headers = {"Authorization": f"Bearer {access_token}"}
    ch_resp = requests.get(ch_url, headers=headers).json()
    
    items = ch_resp.get("items", [])
    if not items:
        print("[-] Could not retrieve channel details. Make sure you selected the channel in browser.")
        return False
        
    channel_info = items[0]
    ch_id = channel_info["id"]
    ch_title = channel_info["snippet"]["title"]
    
    set_key(ENV_PATH, "YOUTUBE_CHANNEL_2_ID", ch_id)
    set_key(ENV_PATH, "YOUTUBE_CHANNEL_2_NAME", ch_title)
    if refresh_token:
        set_key(ENV_PATH, "YOUTUBE_REFRESH_TOKEN_2", refresh_token)
        
    print("\n" + "="*60)
    print("  [SUCCESS] YOUTUBE CHANNEL 2 CONNECTED SUCCESSFULLY!")
    print("="*60)
    print(f"  Channel Title : {ch_title}")
    print(f"  Channel ID    : {ch_id}")
    print(f"  Saved in .env : YOUTUBE_REFRESH_TOKEN_2")
    print("="*60 + "\n")
    return True

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[-] YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET not found in .env")
        sys.exit(1)
        
    scope = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    print("\n" + "="*65)
    print("   CONNECTING CHANNEL 2 (ArisVexx) VIA GOOGLE OAUTH")
    print("="*65)
    print(f"[*] Starting local callback server on port {PORT}...")
    
    server = HTTPServer(("localhost", PORT), OAuthHandler)
    print(f"[*] Opening browser to login:\n{auth_url}\n")
    webbrowser.open(auth_url)
    
    print("[*] Please select 'ArisVexx' channel in your browser...")
    while "code" not in auth_code_holder:
        server.handle_request()
        
    code = auth_code_holder["code"]
    exchange_code_for_tokens(code)

if __name__ == "__main__":
    main()
