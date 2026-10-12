import os
import json
import base64
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key")
    exit(1)

with open("temp_reference/zenitsu_audio.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
prompt = (
    "Listen to this anime fight audio. Transcribe the spoken lines, attacks, and screams with precise timestamps in seconds. "
    "Break into punchy 2-4 word phrases in English. Format strictly as JSON array of objects: "
    '[{"start": 0.5, "end": 2.1, "text": "THUNDER BREATHING"}, {"start": 2.2, "end": 4.5, "text": "FIRST FORM"}]'
)

payload = {
    "contents": [{
        "parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}}
        ]
    }],
    "generationConfig": {"response_mime_type": "application/json"}
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=35) as res:
    data = json.loads(res.read().decode("utf-8"))
    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
    with open("temp_reference/zenitsu_subs.json", "w", encoding="utf-8") as out:
        out.write(raw_json)
    print(raw_json)
