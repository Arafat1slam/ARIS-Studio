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
    # If explicitly passed via CLI
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()
        if arg in ("ch1", "anime", "--ch1", "--anime"):
            return "ch1"
        if arg in ("ch2", "dark", "arisvexx", "--ch2"):
            return "ch2"
        if arg in ("both", "--both", "all"):
            return "both"

    # Otherwise detect based on UTC time (BST is UTC + 6 hours)
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    minute = now_utc.minute
    total_minutes = hour * 60 + minute

    print(f"[*] Cloud Slot Triggered at UTC {now_utc.strftime('%H:%M')} (BST {((hour+6)%24):02d}:{minute:02d})", flush=True)

    # Time windows matching schedule (allowing +/- 20 min buffer for GitHub cron delay)
    # Channel 1: 07:30 UTC (450m), 12:30 UTC (750m), 15:30 UTC (930m)
    # Channel 2: 16:00 UTC (960m), 19:30 UTC (1170m), 00:30 UTC (30m)

    ch1_slots = [450, 750, 930]
    ch2_slots = [30, 960, 1170]

    min_dist_ch1 = min(abs(total_minutes - s) for s in ch1_slots)
    min_dist_ch2 = min(abs(total_minutes - s) for s in ch2_slots)

    if min_dist_ch1 < min_dist_ch2:
        return "ch1"
    else:
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
            "Channel 1 (iταchι Live - Anime Short)"
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
