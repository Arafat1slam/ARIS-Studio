"""
ARIS Custom AI Video Editor
Takes any user video + natural language prompt (Bengali / English)
Uses Gemini AI to intelligently translate prompt into FFmpeg filters,
renders the video with signature high quality, and prepares it for publishing.
"""

import os
import sys
import re
import json
import shutil
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "custom_edits")
TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")

def load_env():
    """Load variables from .env file."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

def get_ffmpeg_bin():
    if os.path.exists(TOOLS_FFMPEG):
        return TOOLS_FFMPEG
    return shutil.which("ffmpeg") or "ffmpeg"

def probe_video(video_path):
    """Inspect duration, dimensions, fps, audio of input video."""
    ffmpeg_bin = get_ffmpeg_bin()
    cmd = [ffmpeg_bin, "-i", video_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    
    info = {
        "duration": 0.0,
        "width": 1920,
        "height": 1080,
        "aspect_ratio": "16:9",
        "has_audio": False,
        "fps": 30.0
    }
    
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", line)
            if m:
                info["duration"] = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
        if "Video:" in line and "x" in line:
            dm = re.search(r",\s*(\d{3,4})x(\d{3,4})", line)
            if dm:
                info["width"] = int(dm.group(1))
                info["height"] = int(dm.group(2))
                if info["height"] > info["width"]:
                    info["aspect_ratio"] = "9:16"
                elif info["width"] == info["height"]:
                    info["aspect_ratio"] = "1:1"
                else:
                    info["aspect_ratio"] = "16:9"
        if "Audio:" in line:
            info["has_audio"] = True
            
    return info

def plan_edit_with_gemini(video_info, user_instruction):
    """
    Use Gemini AI to interpret natural language video edit instructions
    and generate optimal FFmpeg parameters.
    """
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] No GEMINI_API_KEY found, falling back to heuristic parser.", file=sys.stderr)
        return fallback_heuristic_planner(video_info, user_instruction)

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = f"""You are an elite Hollywood video editor and FFmpeg automation engineer.
The user provided a video and an instruction in natural language (Bengali or English).
Translate the user's intent into an accurate, production-grade FFmpeg filter strategy.

Input Video Specs:
- Duration: {video_info['duration']:.2f} seconds
- Resolution: {video_info['width']}x{video_info['height']} ({video_info['aspect_ratio']})
- Has Audio: {video_info['has_audio']}

User's Edit Request:
"{user_instruction}"

Instructions:
1. If the user wants a vertical/Shorts/Reels 9:16 format from a horizontal 16:9 video:
   Use the dark ambient blurred backdrop filter:
   "split[v1][v2];[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];[v2]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,eq=contrast=1.12:saturation=1.2"
2. If the user wants sound enhancement:
   Use audio filters: "atempo=1.04,equalizer=f=110:width_type=h:width=100:g=5,equalizer=f=3500:width_type=h:width=1000:g=3"
3. If the user specifies speed (e.g. 1.2x, 0.8x):
   Set video setpts and audio atempo appropriately.
4. If the user wants cinematic look:
   Add vignette and contrast: "eq=contrast=1.15:saturation=1.2,vignette='PI/4'"
5. If the user specifies trim (e.g. start time, end time, cut):
   Provide "start_time" and "end_time" in "HH:MM:SS" format or null if full duration.

Return ONLY a valid JSON object with the following structure:
{{
  "preset_title": "Short title describing edit in English/Bengali",
  "explanation": "Friendly 1-2 sentence explanation of the edit performed",
  "start_time": null or "00:00:05",
  "end_time": null or "00:00:35",
  "vf": "FFmpeg video filter string (or null)",
  "af": "FFmpeg audio filter string (or null)",
  "speed_factor": 1.0,
  "max_duration": 58
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(raw_text)
    except Exception as e:
        print(f"[!] Gemini planner notice: {e}. Using heuristic fallback.", file=sys.stderr)
        return fallback_heuristic_planner(video_info, user_instruction)

def fallback_heuristic_planner(video_info, user_instruction):
    """Smart heuristic rule parser if Gemini is offline."""
    inst = user_instruction.lower()
    
    # Defaults
    vf_chain = []
    af_chain = []
    start_time = None
    end_time = None
    title = "Custom Video Edit"
    expl = "Applied requested video adjustments."
    
    # 1. Aspect Ratio / Shorts 9:16
    is_shorts_req = any(w in inst for w in ["9:16", "short", "reels", "রিল", "vertical", "লম্বা", "মোবাইল"])
    if is_shorts_req and video_info["aspect_ratio"] != "9:16":
        vf_chain.append("split[v1][v2];[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];[v2]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
        title = "ARIS 9:16 Ambient Short"
        expl = "Converted to 9:16 vertical Canvas with ambient blurred background."
        
    # 2. Color / Cinematic
    if any(w in inst for w in ["cinematic", "color", "contrast", "vivid", "আলোকিত", "সিনেমাটিক", "রং"]):
        vf_chain.append("eq=contrast=1.15:saturation=1.2,vignette='PI/4'")
        expl += " Enhanced contrast, saturation, and cinematic vignette."

    # 3. Audio / Bass
    if any(w in inst for w in ["bass", "sound", "boost", "loud", "সাউন্ড", "গান", "ব্যাস"]):
        af_chain.append("equalizer=f=110:width_type=h:width=100:g=5,equalizer=f=3500:width_type=h:width=1000:g=3")
        expl += " Boosted low-end bass and crisp high-end dialogue."

    # 4. Anti-Copyright Speed micro-shift
    if any(w in inst for w in ["speed", "fast", "গতি", "1.1x", "1.05x"]):
        af_chain.append("atempo=1.05")
        title += " (1.05x Speed Shift)"

    vf_str = ";".join(vf_chain) if vf_chain else None
    af_str = ",".join(af_chain) if af_chain else None

    return {
        "preset_title": title,
        "explanation": expl,
        "start_time": start_time,
        "end_time": end_time,
        "vf": vf_str,
        "af": af_str,
        "speed_factor": 1.0,
        "max_duration": 58
    }

def execute_custom_edit(input_video_path, user_instruction, output_filename=None):
    """
    Main entry point to perform custom edit based on natural language instructions.
    """
    if not os.path.exists(input_video_path):
        return {"success": False, "error": f"Input video not found: {input_video_path}"}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_bin()
    
    print(f"\n{'='*65}\n[*] ARIS AI VIDEO EDITOR: Processing Custom Edit\n{'='*65}")
    print(f"[*] Input File: {os.path.basename(input_video_path)}")
    print(f"[*] User Prompt: \"{user_instruction}\"")
    
    # Step 1: Probe video
    v_info = probe_video(input_video_path)
    print(f"[*] Video Specs: {v_info['width']}x{v_info['height']} | {v_info['duration']:.1f}s | Audio: {v_info['has_audio']}")
    
    # Step 2: AI Plan
    plan = plan_edit_with_gemini(v_info, user_instruction)
    print(f"[+] AI Edit Strategy: {plan.get('preset_title')}")
    print(f"    - Details: {plan.get('explanation')}")
    
    # Step 3: Build FFmpeg command
    ts = int(datetime.utcnow().timestamp())
    out_name = output_filename or f"custom_edit_{ts}.mp4"
    output_path = os.path.join(OUTPUT_DIR, out_name)

    cmd = [ffmpeg_bin, "-y"]
    
    if plan.get("start_time"):
        cmd.extend(["-ss", str(plan["start_time"])])
    if plan.get("end_time"):
        cmd.extend(["-to", str(plan["end_time"])])
    elif plan.get("max_duration") and v_info["duration"] > plan["max_duration"]:
        cmd.extend(["-t", str(plan["max_duration"])])

    cmd.extend(["-i", input_video_path])

    # Filters
    vf = plan.get("vf")
    if vf:
        cmd.extend(["-filter_complex", vf] if ";" in vf else ["-vf", vf])
    else:
        # Default high-quality remux
        cmd.extend(["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"])

    af = plan.get("af")
    if af and v_info["has_audio"]:
        cmd.extend(["-af", af])

    # Quality settings
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ])

    print(f"[*] Running FFmpeg engine...", flush=True)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")

    if res.returncode != 0 or not os.path.exists(output_path):
        print(f"[-] FFmpeg error: {res.stderr[-500:]}", file=sys.stderr)
        return {"success": False, "error": res.stderr[-500:], "plan": plan}

    out_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    out_info = probe_video(output_path)
    print(f"[+] Success! Edited Video Saved: {output_path} ({out_size_mb:.2f} MB)")

    return {
        "success": True,
        "output_path": output_path,
        "filename": os.path.basename(output_path),
        "size_mb": round(out_size_mb, 2),
        "duration": out_info["duration"],
        "resolution": f"{out_info['width']}x{out_info['height']}",
        "plan": plan
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python custom_ai_editor.py <input_video.mp4> <instruction_prompt>")
        sys.exit(1)
        
    in_video = sys.argv[1]
    instruction = sys.argv[2]
    result = execute_custom_edit(in_video, instruction)
    print(json.dumps(result, indent=2))
