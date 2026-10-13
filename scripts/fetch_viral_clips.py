"""
ARIS Anime Clip Auto-Downloader
Fetches high-quality, viral anime clips directly on local PC (residential IP)
and prepares them in data/approved_clips/ for GitHub Actions Cloud Autopilot.
"""

import os
import sys
import glob
import re

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import clip_downloader
import duplicate_checker

def sanitize_filename(filepath):
    dname = os.path.dirname(filepath)
    bname = os.path.basename(filepath)
    clean_name = re.sub(r'[^\w\s\.-]', '_', bname)
    clean_name = re.sub(r'\s+', '_', clean_name).strip('_')
    new_path = os.path.join(dname, clean_name)
    if new_path != filepath and not os.path.exists(new_path):
        os.rename(filepath, new_path)
        return new_path
    return filepath

def fetch_fresh_batch(count=3):
    print("=" * 60)
    print(f"[*] ARIS SOURCING ENGINE: Fetching {count} fresh viral anime clips...")
    print("=" * 60)
    
    res = clip_downloader.auto_fetch_viral_batch(count=count)
    fetched = res.get("fetched_count", 0)
    print(f"\n[+] Total fetched: {fetched}")
    
    # Sanitize names and check duplicates
    approved_dir = os.path.join(PROJECT_DIR, "data", "approved_clips")
    for mp4 in glob.glob(os.path.join(approved_dir, "*.mp4")):
        clean = sanitize_filename(mp4)
        bname = os.path.basename(clean)
        is_dup, _ = duplicate_checker.is_duplicate(bname)
        if is_dup:
            print(f"[!] Removing duplicate: {bname}")
            try:
                os.remove(clean)
            except Exception:
                pass
        else:
            print(f"[OK] Ready for cloud queue: {bname}")

    print("\n" + "=" * 60)
    print("[+] All approved clips are ready in data/approved_clips/!")
    print("[*] To sync with GitHub Cloud Autopilot, just run:")
    print("    git add data/approved_clips/ && git commit -m 'feat: add fresh anime clips' && git push")
    print("=" * 60)

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    fetch_fresh_batch(count)
