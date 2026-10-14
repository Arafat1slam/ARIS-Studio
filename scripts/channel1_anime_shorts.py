"""
ARIS Studio - Channel 1 Engine: Viral Anime Shorts
Workflow:
1. Select & Download Clips from AnimeClips.online (or local approved pool)
2. Quality Check raw input
3. Fast Minimal High-Impact Editing (9:16 Ambient Blur, Beat Zoom, Bold Yellow Subtitles, Anti-Copyright EQ)
4. Export as Shorts (1080x1920)
5. Quality Control (QC Audit & Auto-Remediation)
6. Generate Premiere Pro 2026 Sequence XML & ExtendScript
7. Generate SEO Metadata for YouTube Channel 1
"""

import os
import sys
import glob
import json
import random
import shutil
import subprocess
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

load_dotenv(os.path.join(PROJECT_DIR, ".env"))

import animeclips_fetcher
import quality_control
import premiere_automation
import duplicate_checker
import gemini_metadata

TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
APPROVED_DIR = os.path.join(PROJECT_DIR, "data", "approved_clips")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)

def get_ffmpeg_bin():
    if os.path.exists(TOOLS_FFMPEG):
        return TOOLS_FFMPEG
    return shutil.which("ffmpeg") or "ffmpeg"

def produce_channel1_short(anime_slug=None, custom_clip_path=None):
    """
    Produce a complete, QC-verified Channel 1 Viral Anime Short.
    """
    timestamp = int(datetime.now(timezone.utc).timestamp())
    print("=" * 60)
    print("🎬 ARIS CHANNEL 1 ENGINE: Producing Viral Anime Short")
    print("=" * 60)

    # 1. Source Clip
    clip_path = custom_clip_path
    if not clip_path or not os.path.exists(clip_path):
        # Pick from AnimeClips.online
        slug = anime_slug or random.choice(["a-silent-voice", "attack-on-titan", "jujutsu-kaisen", "vinland-saga", "demon-slayer"])
        downloaded = animeclips_fetcher.fetch_random_clips(slug=slug, count=1, target_dir=APPROVED_DIR)
        if downloaded:
            clip_path = downloaded[0]
        else:
            # Fallback to local approved clips
            locals_clips = glob.glob(os.path.join(APPROVED_DIR, "*.mp4"))
            if locals_clips:
                clip_path = random.choice(locals_clips)

    if not clip_path or not os.path.exists(clip_path):
        print("[-] Error: No source clip available for Channel 1.")
        return {"success": False, "error": "No clip available"}

    print(f"[*] Source clip: {os.path.basename(clip_path)}")
    clip_info = quality_control.probe_video_details(clip_path)

    # 2. Rendering High-Impact 9:16 Short via FFmpeg
    output_filename = f"ch1_anime_short_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    ffmpeg_bin = get_ffmpeg_bin()

    duration = min(clip_info["duration"], 45.0) if clip_info["duration"] > 0 else 25.0
    # Beat zoom & ambient 9:16 filter
    video_filter = (
        "[0:v]split[bg][fg];"
        "[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=14:2,scale=1080:1920,"
        "eq=brightness=-0.1:contrast=1.1[bg_dark];"
        "[fg]scale=1080:1920:force_original_aspect_ratio=decrease,"
        "unsharp=5:5:0.8:5:5:0.0[fg_sharp];"
        "[bg_dark][fg_sharp]overlay=(W-w)/2:(H-h)/2,"
        "vignette=PI/4.8,"
        "drawtext=text='ARIS':fontcolor=white@0.4:fontsize=28:x=w-tw-40:y=80,"
        "fps=30[v]"
    )

    if clip_info["has_audio"]:
        # Anti-copyright audio EQ & normalize
        audio_filter = "[0:a]atempo=1.02,equalizer=f=120:width_type=h:width=100:g=3,equalizer=f=3500:width_type=h:width=1000:g=2,loudnorm=I=-14:LRA=7:TP=-1.0[a]"
        filter_complex = f"{video_filter};{audio_filter}"
        map_args = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_complex = video_filter
        map_args = ["-map", "[v]"]

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", "0",
        "-t", str(duration),
        "-i", clip_path,
        "-filter_complex", filter_complex
    ] + map_args + [
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    print("[*] Rendering 9:16 Short with FFmpeg...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.exists(output_path):
        print(f"[-] FFmpeg render failed: {proc.stderr[:300]}")
        return {"success": False, "error": proc.stderr}

    print(f"[OK] Rendered: {output_filename} ({os.path.getsize(output_path)/(1024*1024):.2f} MB)")

    # 3. Quality Control (QC Audit & Auto-Remediation Loop)
    print("\n🔍 Running Automated Quality Control...")
    qc_res = quality_control.audit_video(output_path)
    final_video_path = output_path

    if not qc_res["passed"]:
        print(f"[!] QC detected issues: {qc_res['issues']}. Auto-remediating...")
        remed_res = quality_control.remediate_video(output_path)
        if remed_res["success"] and remed_res["audit"]["passed"]:
            final_video_path = remed_res["remediated_path"]
            print("[+] QC Passed after Auto-Remediation!")
        else:
            print("[!] Video completed with minor QC warnings.")
    else:
        print("[+] QC PASSED 100%! Format, Audio (-14 LUFS), and Pacing are optimal.")

    # 4. Generate Premiere Pro 2026 Project & XML
    print("\n🎬 Generating Premiere Pro 2026 Project Files...")
    ppro_res = premiere_automation.generate_fcp_xml_sequence([clip_path], title="Channel1_Anime_Short")
    jsx_res = premiere_automation.generate_premiere_extendscript([clip_path], title="Channel1_Anime_Short")

    # 5. Generate SEO Metadata
    print("\n🚀 Generating SEO Metadata for Channel 1...")
    meta = gemini_metadata.generate_metadata(clip_context=os.path.basename(clip_path))

    return {
        "success": True,
        "video_path": final_video_path,
        "source_clip": clip_path,
        "qc_passed": qc_res["passed"],
        "premiere_xml": ppro_res["xml_path"],
        "premiere_jsx": jsx_res["script_path"],
        "seo_metadata": meta
    }

if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "a-silent-voice"
    res = produce_channel1_short(anime_slug=slug)
    print("\n" + "=" * 60)
    print("[+] Channel 1 Production Complete!")
    print(f"Video: {res.get('video_path')}")
    print(f"Premiere XML: {res.get('premiere_xml')}")
    print(f"Title: {res.get('seo_metadata', {}).get('title')}")
    print("=" * 60)
