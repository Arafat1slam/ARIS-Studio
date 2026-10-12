import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)

SCHEDULE_SLOTS = [
    # Channel 1: iταchι Live (Anime & Website CTA)
    {
        "time": "13:30",
        "channel": "iταchι Live",
        "script": "scripts/pipeline_orchestrator.py",
        "args": ["--auto"],
        "desc": "Anime Short: Midday Lunch Scroll"
    },
    {
        "time": "18:30",
        "channel": "iταchι Live",
        "script": "scripts/pipeline_orchestrator.py",
        "args": ["--auto"],
        "desc": "Anime Short: Evening Peak"
    },
    {
        "time": "21:30",
        "channel": "iταchι Live",
        "script": "scripts/pipeline_orchestrator.py",
        "args": ["--auto"],
        "desc": "Anime Short: Night Prime Time"
    },
    # Channel 2: ArisVexx (Dark Psychology / USA High-CPM Target)
    {
        "time": "22:00",
        "channel": "ArisVexx",
        "script": "scripts/dark_psychology_generator.py",
        "args": [],
        "desc": "Dark Psychology: US Noon Lunch (12:00 PM EST)"
    },
    {
        "time": "01:30",
        "channel": "ArisVexx",
        "script": "scripts/dark_psychology_generator.py",
        "args": [],
        "desc": "Dark Psychology: US Afternoon Break (03:30 PM EST)"
    },
    {
        "time": "06:30",
        "channel": "ArisVexx",
        "script": "scripts/dark_psychology_generator.py",
        "args": [],
        "desc": "Dark Psychology: US Prime Golden Hour (08:30 PM EST)"
    }
]

def get_next_slot():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    candidates = []
    for slot in SCHEDULE_SLOTS:
        dt = datetime.strptime(f"{today_str} {slot['time']}", "%Y-%m-%d %H:%M")
        if dt > now:
            candidates.append((dt, slot))
            
    if not candidates:
        tomorrow = now + timedelta(days=1)
        tmrw_str = tomorrow.strftime("%Y-%m-%d")
        for slot in SCHEDULE_SLOTS:
            dt = datetime.strptime(f"{tmrw_str} {slot['time']}", "%Y-%m-%d %H:%M")
            candidates.append((dt, slot))
            
    candidates.sort(key=lambda x: x[0])
    return candidates[0]

def execute_slot(slot: dict):
    print("\n" + "="*68)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TRIGGERING SCHEDULED SLOT: {slot['channel'].upper()}")
    print("="*68)
    print(f"[*] Target Channel : {slot['channel']}")
    print(f"[*] Slot Name      : {slot['desc']}")
    print(f"[*] Engine Script  : {slot['script']}")
    print("="*68 + "\n")
    
    cmd = [sys.executable, slot["script"]] + slot.get("args", [])
    try:
        subprocess.run(cmd, check=True)
        print(f"\n[+] Execution completed successfully for {slot['channel']} at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"\n[-] Slot execution issue: {e}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("====================================================================")
    print("   ARIS CONTENT AUTOMATION SYSTEM - DUAL-CHANNEL 24/7 AUTO PILOT    ")
    print("====================================================================")
    print("  Channel 1 : iταchι Live  [Anime Clips -> anime.ariswork.site]")
    print("              Slots: 01:30 PM | 06:30 PM | 09:30 PM (BST)")
    print("  Channel 2 : ArisVexx     [Dark Psychology -> USA High-CPM Target]")
    print("              Slots: 10:00 PM | 01:30 AM | 06:30 AM (BST = US PEAK)")
    print("  Policy    : Fully autonomous sourcing, AI SEO, upload & cleanup")
    print("====================================================================\n")
    
    last_triggered_minute = None
    
    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_minute_str = now.strftime("%Y-%m-%d %H:%M")
        
        # Check if current time matches any scheduled slot
        for slot in SCHEDULE_SLOTS:
            if current_time_str == slot["time"] and last_triggered_minute != current_minute_str:
                last_triggered_minute = current_minute_str
                print(f"\n\n[TIME HIT] {slot['time']} ({slot['desc']}) triggered!")
                execute_slot(slot)
                break
                
        next_dt, next_slot = get_next_slot()
        remaining = next_dt - datetime.now()
        rem_sec = max(0, int(remaining.total_seconds()))
        hours, rem = divmod(rem_sec, 3600)
        minutes, seconds = divmod(rem, 60)
        countdown = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
        
        status_line = (
            f"\r[*] Current: {now.strftime('%I:%M:%S %p')} | "
            f"Next: [{next_slot['channel']}] in {countdown} ({next_dt.strftime('%I:%M %p')}) | "
            f"Status: STANDBY (Auto) "
        )
        sys.stdout.write(status_line)
        sys.stdout.flush()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Auto Pilot stopped by user.")
