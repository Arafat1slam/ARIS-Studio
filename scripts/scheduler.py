import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORCHESTRATOR_PATH = os.path.join(PROJECT_DIR, "scripts", "pipeline_orchestrator.py")

# Target schedule: 1:30 PM, 6:30 PM, 9:30 PM
SCHEDULE_TIMES = [
    ("13:30", "Midday Lunch Scroll"),
    ("18:30", "Evening Peak"),
    ("21:30", "Night Prime Time")
]

def get_next_run():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    candidates = []
    for t_str, desc in SCHEDULE_TIMES:
        dt = datetime.strptime(f"{today_str} {t_str}", "%Y-%m-%d %H:%M")
        if dt > now:
            candidates.append((dt, desc))
    
    if not candidates:
        # Tomorrow's first slot
        tomorrow = now + timedelta(days=1)
        t_str, desc = SCHEDULE_TIMES[0]
        dt = datetime.strptime(f"{tomorrow.strftime('%Y-%m-%d')} {t_str}", "%Y-%m-%d %H:%M")
        return dt, desc
    
    candidates.sort(key=lambda x: x[0])
    return candidates[0]

def execute_pipeline():
    print("\n" + "="*65)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TRIGGERING AUTOMATED CONTENT PIPELINE")
    print("="*65)
    print("[*] 1. Sourcing trending 4K viral anime clip...")
    print("[*] 2. Remastering 1080x1920 anti-copyright canvas + audio...")
    print("[*] 3. Generating viral AI SEO tags & description via Gemini...")
    print("[*] 4. Publishing to YouTube Shorts & updating duplicate ledger...")
    print("[*] 5. Auto-deleting local files to save disk space...")
    print("="*65 + "\n")
    
    try:
        proc = subprocess.run(
            [sys.executable, ORCHESTRATOR_PATH, "--auto"],
            cwd=PROJECT_DIR,
            check=True
        )
        print(f"\n[+] Pipeline completed successfully at {datetime.now().strftime('%H:%M:%S')}")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Pipeline encountered an issue: {e}")
    except Exception as e:
        print(f"\n[-] Unexpected error during execution: {e}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===================================================================")
    print("        ARIS CONTENT AUTOMATION SYSTEM - 24/7 AUTO SCHEDULER       ")
    print("===================================================================")
    print("  YouTube Channel : iταchι Live")
    print("  Website CTA     : https://anime.ariswork.site")
    print("  Schedule Slots  : 01:30 PM | 06:30 PM | 09:30 PM (Asia/Dhaka)")
    print("  Storage Policy  : Auto-deletes videos after upload")
    print("===================================================================\n")
    
    last_triggered_minute = None
    
    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_minute_str = now.strftime("%Y-%m-%d %H:%M")
        
        # Check if current time matches any scheduled slot
        for t_str, desc in SCHEDULE_TIMES:
            if current_time_str == t_str and last_triggered_minute != current_minute_str:
                last_triggered_minute = current_minute_str
                print(f"\n[TIME HIT] Scheduled slot: {t_str} ({desc})! Executing now...")
                execute_pipeline()
                break
        
        next_dt, next_desc = get_next_run()
        remaining = next_dt - datetime.now()
        rem_sec = max(0, int(remaining.total_seconds()))
        hours, rem = divmod(rem_sec, 3600)
        minutes, seconds = divmod(rem, 60)
        countdown = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
        
        status_line = (
            f"\r[*] Current: {now.strftime('%I:%M:%S %p')} | "
            f"Next Upload: {next_dt.strftime('%I:%M %p')} ({next_desc}) in [{countdown}] | "
            f"Status: STANDBY (Auto) "
        )
        sys.stdout.write(status_line)
        sys.stdout.flush()
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Scheduler stopped by user.")
