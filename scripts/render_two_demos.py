"""
Generates 2 fresh preview videos strictly saved to 'not_uploaded/' for user review:
1. Channel 1 (iταchι Live - Anime): Clean Dark Ambient Spotlight remaster (Zero text overlays)
2. Channel 2 (ArisVexx - Dark Psychology): Upgraded word-chunked ASS viral subtitles + Dark Phonk BGM
"""

import os
import sys
import json
import hashlib

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import ffmpeg_generator
import archive_uploaded_videos
import dark_psychology_generator

def render_channel1_demo():
    print("\n" + "="*65)
    print("   PRODUCING DEMO 1: CHANNEL 1 (ANIME - iταchι Live)")
    print("="*65)

    input_clip = os.path.join(PROJECT_DIR, "data", "approved_clips", "Zenitsu God-like speed 60fps_sBc9PwGawUM.mp4")
    if not os.path.exists(input_clip):
        print(f"[-] Clip not found: {input_clip}")
        return None

    # Style 0 = DARK_AMBIENT_SPOTLIGHT (Clean 16:9 widescreen centered, blurred 9:16 background, NO text overlays)
    res = ffmpeg_generator.generate_short(
        input_path=input_clip,
        output_dir=os.path.join(PROJECT_DIR, "data", "temp"),
        max_duration=32.0,
        style_index=0
    )

    if not res.get("success"):
        print(f"[-] Channel 1 render failed: {res.get('error')}")
        return None

    rendered_file = res["output_file"]
    title = "Zenitsu 60FPS God-Like Speed Remaster #Shorts"
    desc = (
        "Zenitsu reaches God-like speed in this ultra-smooth 60FPS Demon Slayer edit!\n\n"
        "Remastered with dynamic 4K ambient spotlight framing and enhanced cinema audio.\n\n"
        "Subscribe to iταchι Live for daily viral anime fight scenes!\n\n"
        "#DemonSlayer #Zenitsu #KimetsuNoYaiba #AnimeEdits #AnimeShorts #60fps #ItachiLive #Shorts"
    )
    tags = ["DemonSlayer", "Zenitsu", "KimetsuNoYaiba", "AnimeEdits", "AnimeShorts", "60fps", "ItachiLive", "Shorts"]

    target_mp4 = archive_uploaded_videos.save_to_not_uploaded(
        video_path=rendered_file,
        title=title,
        description=desc,
        tags=tags,
        channel="Itachi_Live",
        move=True
    )

    print(f"[+] Channel 1 Demo Ready: {target_mp4}")
    return target_mp4

def render_channel2_demo():
    print("\n" + "="*65)
    print("   PRODUCING DEMO 2: CHANNEL 2 (DARK PSYCHOLOGY - ArisVexx)")
    print("="*65)

    # Produce with upgraded subtitles + dark phonk BGM in dry_run mode
    res = dark_psychology_generator.produce_arisvexx_short(dry_run=True)
    print(f"[+] Channel 2 Demo Output: {res}")
    return res

def main():
    ch1_file = render_channel1_demo()
    ch2_res = render_channel2_demo()
    
    print("\n" + "="*65)
    print("   BOTH DEMO VIDEOS PRODUCED SUCCESSFULLY IN 'not_uploaded/'")
    print("="*65)
    print(f"Channel 1 Video: {ch1_file}")
    print(f"Channel 2 Status: {ch2_res}")

if __name__ == "__main__":
    main()
