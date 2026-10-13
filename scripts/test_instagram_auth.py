import os
import sys
import json
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired,
    TwoFactorRequired,
    BadPassword,
    PleaseWaitFewMinutes,
    LoginRequired
)

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SESSION_FILE = os.path.join(PROJECT_DIR, "config", "instagram_session.json")
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

USERNAME = os.getenv("INSTAGRAM_USERNAME", "").strip()
PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "").strip()

print(f"[*] Testing Instagram authentication for: {USERNAME}")

if not USERNAME or not PASSWORD:
    print("[-] Missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD in .env")
    sys.exit(1)

cl = Client()
cl.delay_range = [1, 3]

# 1. Try loading saved session first if exists
if os.path.exists(SESSION_FILE):
    print(f"[*] Found existing session file: {SESSION_FILE}")
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()
        print("[+] Session loaded and validated successfully!")
        user_info = cl.user_info(cl.user_id)
        print(f"[+] Logged in as: @{user_info.username} ({user_info.full_name})")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Saved session expired or invalid: {e}. Re-authenticating...")

# 2. Fresh login with username & password
try:
    print("[*] Initiating login with credentials...")
    cl.login(USERNAME, PASSWORD)
    print("[+] Login successful!")
    
    # Save settings to session file
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    cl.dump_settings(SESSION_FILE)
    print(f"[+] Saved session settings to: {SESSION_FILE}")
    
    user_info = cl.user_info(cl.user_id)
    print(f"[+] Logged in as: @{user_info.username} (ID: {cl.user_id})")
    print(f"[+] Account Handle: @{user_info.username}")
    print("[+] Instagram integration is 100% verified and ready!")
except TwoFactorRequired:
    print("[!] Two-Factor Authentication (2FA) is required on this account.")
    print("[!] Please check your phone / authenticator app for the 6-digit code.")
    sys.exit(2)
except ChallengeRequired as cr:
    print(f"[!] Instagram Security Challenge Required: {cr}")
    print("[!] Instagram sent a verification code to your phone or email, or requires 'This was me' in app.")
    sys.exit(3)
except BadPassword:
    print("[-] Incorrect password provided.")
    sys.exit(4)
except PleaseWaitFewMinutes:
    print("[-] Instagram rate-limit: Please wait a few minutes before trying again.")
    sys.exit(5)
except Exception as e:
    print(f"[-] Login failed with error: {type(e).__name__}: {e}")
    sys.exit(1)
