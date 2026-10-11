import os
import sys
import secrets
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(ENV_PATH)

CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')
CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8080/callback"
PORT = 8080

auth_code_holder = {}

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        if 'code' in query_components:
            auth_code_holder['code'] = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
            <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#121212; color:#fff;">
                <h1 style="color:#00f2fe;">TikTok Authentication Successful!</h1>
                <p>Tokens received and saved to .env. You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif 'error' in query_components:
            err = query_components.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"<h1>Error during TikTok login: {err}</h1>".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress default server logs

def exchange_code_for_token(code: str):
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    print("[*] Exchanging authorization code for TikTok access and refresh tokens...")
    resp = requests.post(token_url, data=payload, headers=headers)
    data = resp.json()

    if resp.status_code == 200 and 'access_token' in data:
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        open_id = data.get('open_id')
        expires_in = data.get('expires_in')

        set_key(ENV_PATH, "TIKTOK_ACCESS_TOKEN", access_token)
        if refresh_token:
            set_key(ENV_PATH, "TIKTOK_REFRESH_TOKEN", refresh_token)
        if open_id:
            set_key(ENV_PATH, "TIKTOK_OPEN_ID", open_id)

        print("[SUCCESS] TikTok OAuth tokens obtained successfully!")
        print(f"[*] Open ID: {open_id}")
        print(f"[*] Access Token Expires in: {expires_in}s")
        print("[*] Saved TIKTOK_ACCESS_TOKEN and TIKTOK_REFRESH_TOKEN to .env")
        return True
    else:
        print(f"[ERROR] Failed to exchange token: {data}")
        return False

def main():
    if not CLIENT_KEY or not CLIENT_SECRET:
        print("[ERROR] TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET missing from .env!")
        sys.exit(1)

    csrf_state = secrets.token_urlsafe(16)
    scopes = "user.info.basic,video.upload,video.publish"
    
    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&scope={scopes}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={csrf_state}"
    )

    print("\n" + "="*60)
    print("   TIKTOK OAUTH AUTHENTICATION SETUP")
    print("="*60)
    print(f"[*] Starting local server on port {PORT} to intercept callback...")
    
    server = HTTPServer(('localhost', PORT), OAuthHandler)
    print(f"[*] Opening browser to TikTok login:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("[*] Waiting for user authorization in browser...")
    while 'code' not in auth_code_holder:
        server.handle_request()

    code = auth_code_holder['code']
    print(f"[+] Authorization code captured: {code[:10]}...")
    success = exchange_code_for_token(code)
    if success:
        print("\n[COMPLETE] TikTok setup is ready for auto-publishing!\n")
    else:
        print("\n[FAIL] Could not complete TikTok authorization.\n")

if __name__ == '__main__':
    main()
