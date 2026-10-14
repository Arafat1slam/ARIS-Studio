import urllib.request
import re
import sys
import json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

url = "https://www.youtube.com/watch?v=z88Y1p5RXR4"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")

# Find description and chapters
desc_match = re.search(r'"description":\{"simpleText":"(.*?)"\}', html)
if not desc_match:
    desc_match = re.search(r'"shortDescription":"(.*?)"', html)
if desc_match:
    desc = desc_match.group(1).encode('utf-8').decode('unicode_escape', errors='ignore')
    print("Video Description:\n", desc)

# Search for chapters in html
chapters = re.findall(r'(\d{1,2}:\d{2})\s+-\s+([^"\<\n]+)', html)
print("\nChapters:", chapters[:15])
