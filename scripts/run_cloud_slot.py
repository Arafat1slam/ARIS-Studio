import os
import sys
import subprocess
from datetime import datetime, timezone

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)

def run_command(cmd, desc):
    print(f"\n{'='*65}\n[*] RUNNING: {desc}\n{'='*65}", flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    if res.stdout:
        print(res.stdout, flush=True)
    
    # Save log to data/logs/autopilot_run.log for persistence
    log_file = os.path.join(PROJECT_DIR, "data", "logs", "autopilot_run.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as lf:
        lf.write(f"\n{'='*65}\n[{datetime.utcnow().isoformat()}] {desc}\n{'='*65}\n")
        lf.write(res.stdout or "")
        lf.write(f"\nExit Code: {res.returncode}\n")

    if res.returncode != 0:
        print(f"[-] Command failed with exit code {res.returncode}", flush=True)
        return False
    return True

def determine_target():
    # If explicitly passed via CLI or GitHub Actions input
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()
        if arg in ("ch1", "anime", "--ch1", "--anime"):
            print("[*] Target explicitly set: CHANNEL 1 (iταchι Live Anime + Instagram Reels + FB)", flush=True)
            return "ch1"
        if arg in ("ch2", "dark", "arisvexx", "--ch2"):
            print("[*] Target explicitly set: CHANNEL 2 (ArisVexx Dark Psychology)", flush=True)
            return "ch2"
        if arg in ("both", "--both", "all"):
            print("[*] Target explicitly set: BOTH CHANNELS", flush=True)
            return "both"
        # If 'auto', proceed to schedule detection below

    # Check if triggered by GitHub Actions cron schedule
    sched_cron = os.getenv("GITHUB_EVENT_SCHEDULE", "").strip()
    if sched_cron:
        ch1_crons = {"30 7 * * *", "32 7 * * *", "30 12 * * *", "32 12 * * *", "30 15 * * *", "32 15 * * *"}
        ch2_crons = {"00 16 * * *", "03 16 * * *", "30 19 * * *", "33 19 * * *", "30 0 * * *", "32 0 * * *"}
        if sched_cron in ch1_crons:
            print(f"[*] Triggered by Channel 1 Scheduled Cron: '{sched_cron}'", flush=True)
            return "ch1"
        if sched_cron in ch2_crons:
            print(f"[*] Triggered by Channel 2 Scheduled Cron: '{sched_cron}'", flush=True)
            return "ch2"

    # Automated Schedule or 'auto' based on UTC/BST Time brackets:
    # Channel 1 (Anime + Instagram): 06:00 UTC to 15:45 UTC (12:00 PM to 09:45 PM BST)
    # Channel 2 (ArisVexx): 15:45 UTC to 05:59 UTC (09:45 PM to 11:59 AM BST)
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    minute = now_utc.minute
    total_minutes = hour * 60 + minute

    bst_hour = (hour + 6) % 24
    print(f"[*] Cloud Slot Detection at UTC {now_utc.strftime('%H:%M')} (BST {bst_hour:02d}:{minute:02d})", flush=True)

    # 06:00 UTC = 360m, 15:45 UTC = 945m
    if 360 <= total_minutes < 945:
        print("[*] Current slot falls inside Channel 1 window (Day/Evening BST)", flush=True)
        return "ch1"
    else:
        print("[*] Current slot falls inside Channel 2 window (USA Prime Night/Bedtime)", flush=True)
        return "ch2"

def main():
    target = determine_target()
    print(f"[*] Target selected: {target.upper()}", flush=True)

    # Pre-flight environment diagnostics
    env_file = os.path.join(PROJECT_DIR, ".env")
    print(f"[*] Environment Diagnostics:", flush=True)
    print(f"    - .env exists: {os.path.exists(env_file)}", flush=True)
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"    - GEMINI_API_KEY set: {bool(os.getenv('GEMINI_API_KEY'))}", flush=True)
        print(f"    - YOUTUBE_CLIENT_ID_2 set: {bool(os.getenv('YOUTUBE_CLIENT_ID_2'))}", flush=True)
        print(f"    - YOUTUBE_REFRESH_TOKEN_2 set: {bool(os.getenv('YOUTUBE_REFRESH_TOKEN_2'))}", flush=True)
        broll_count = len([f for f in os.listdir(os.path.join(PROJECT_DIR, 'data', 'broll')) if f.endswith('.mp4')])
        print(f"    - B-Roll clips count: {broll_count}", flush=True)
    except Exception as de:
        print(f"    [!] Diagnostics notice: {de}", flush=True)

    success = True
    if target in ("ch1", "both"):
        ok = run_command(
            [sys.executable, "-u", "scripts/pipeline_orchestrator.py", "--auto"],
            "Channel 1 (iταchι Live - Anime Short, Instagram Reel & FB)"
        )
        success = success and ok

    if target in ("ch2", "both"):
        ok = run_command(
            [sys.executable, "-u", "scripts/dark_psychology_generator.py", "--auto"],
            "Channel 2 (ArisVexx - Dark Psychology Short)"
        )
        success = success and ok

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
