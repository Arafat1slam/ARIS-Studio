import urllib.request
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def check_packs(scp_id):
    url = f"https://scenepacks.com/scps/{scp_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
    matches = re.findall(r'href=["\']/download/(\d+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
    print(f"\n=== Packs for {scp_id} ===")
    for dl_id, t in matches[:10]:
        clean = re.sub(r'<[^>]+>', ' ', t).strip()
        clean = re.sub(r'\s+', ' ', clean)
        print(f" - DL ID {dl_id}: {clean}")

check_packs(186)
check_packs(187)
