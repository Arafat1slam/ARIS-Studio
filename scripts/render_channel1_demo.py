"""
Render Channel 1 (iταchι Live) Anime Master Short.
Transforms Levi Ackerman / Attack on Titan clip with:
- 4K Razor-sharp visual grading & 9:16 vertical remaster
- High-energy Phonk music layering with anime combat audio & sound effects
- Glowing hook badge + kinetic lower-third typography
- Saves directly to 'not_uploaded/' with companion caption info.txt
- ZERO auto-upload (Ready for user review)
"""

import os
import sys
import json

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import ffmpeg_generator
import archive_uploaded_videos

def render_anime_master():
    input_clip = os.path.join(PROJECT_DIR, "data", "approved_clips", "Levi VS The ancient 9 Titans _ AOT Final Part _ 4K_zAxb4wHcL_k.mp4")
    if not os.path.exists(input_clip):
        # Fallback to Zenitsu clip if Levi is not present
        candidates = [
            os.path.join(PROJECT_DIR, "data", "approved_clips", "Zenitsu GODSPEED (Demon Slayer Edit)_VilPPB6xrzw.mp4"),
            os.path.join(PROJECT_DIR, "data", "approved_clips", "Zenitsu God-like speed 60fps_sBc9PwGawUM.mp4")
        ]
        for c in candidates:
            if os.path.exists(c):
                input_clip = c
                break

    print(f"[*] Sourcing input clip: {os.path.basename(input_clip)}")
    
    # Render with upgraded ffmpeg_generator (Phonk + kinetic ASS subtitles)
    res = ffmpeg_generator.generate_short(
        input_path=input_clip,
        output_dir=os.path.join(PROJECT_DIR, "data", "temp"),
        max_duration=29.0,
        style_index=0  # Action Fullscreen 9:16
    )

    if not res.get("success"):
        print(f"[-] Render failed: {res.get('error')}", file=sys.stderr)
        return res

    rendered_file = res["output_file"]
    title = "Levi Ackerman VS The Ancient 9 Titans - Absolute God Mode 4K"
    desc = (
        "Humanity's strongest soldier Levi Ackerman unleashes absolute God Mode against the Ancient 9 Titans!\n\n"
        "Remastered in 4K 60fps with high-energy Phonk music and dynamic typography.\n\n"
        "Subscribe to iταchι Live for daily viral anime fight scenes and edits!\n\n"
        "#AttackOnTitan #LeviAckerman #AOT #AnimeShorts #AnimeEdits #Phonk #ItachiLive #Shorts"
    )
    tags = ["AttackOnTitan", "LeviAckerman", "AOT", "AnimeShorts", "AnimeEdits", "Phonk", "ItachiLive", "Shorts"]

    # Save to 'not_uploaded/'
    target_mp4 = archive_uploaded_videos.save_to_not_uploaded(
        video_path=rendered_file,
        title=title,
        description=desc,
        tags=tags,
        channel="Itachi_Live",
        move=True
    )

    print(f"\n[+] SUCCESS! New Anime Master Video produced:")
    print(f"    Video: {target_mp4}")
    print(f"    Info : {target_mp4.replace('.mp4', '_info.txt')}")
    print(f"    Phonk Beat: {res.get('phonk_track')}")
    print(f"    Duration: {res.get('duration')}s")

    return {
        "success": True,
        "video_file": target_mp4,
        "info_file": target_mp4.replace(".mp4", "_info.txt"),
        "phonk_track": res.get("phonk_track"),
        "duration": res.get("duration")
    }

if __name__ == "__main__":
    out = render_anime_master()
    print(json.dumps(out, indent=2))
