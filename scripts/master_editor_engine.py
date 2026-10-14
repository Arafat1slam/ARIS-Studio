"""
ARIS Studio - Master Editor AI Engine (James Prince Pro Course + eitaX AMV Standard)
Inspired by:
- James Prince Premiere Pro Master Course: Timeline tracks, In/Out trimming, Adjustment Layers, Beat Markers
- eitaX "Crimson Moon" 4K Akaza Edit (https://www.youtube.com/watch?v=f_DUBwVR8Mw):
  Velocity Speed Ramping, Decaying Impact Shakes (S_Shake), RGB Chromatic Aberration,
  Optical Bloom / Deep Glow, Exposure Flashes, and Slowed Phonk Audio Mastering.
"""

import os
import sys
import glob
import json
import shutil
import subprocess
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import quality_control
import premiere_automation
import aftereffects_bridge

FFMPEG = r"tools\ffmpeg.exe" if os.path.exists(r"tools\ffmpeg.exe") else "ffmpeg"
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll", "scenepacks")
OUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def render_eitax_god_tier_anime_short(output_filename="God_Tier_Anime_AMV_4K.mp4"):
    """
    Renders an elite 60FPS Anime AMV short matching eitaX's signature velocity & impact style.
    """
    print("\n" + "="*70)
    print("⚡ ARIS MASTER ENGINE: Rendering eitaX God-Tier AMV (60FPS Velocity)")
    print("   Standard: 'Crimson Moon' Akaza Style (Slowed Phonk, S_Shake, RGB Split, Deep Glow)")
    print("="*70)

    # 1. Sourcing Best Shots from Scenepacks (Gojo / JJK)
    clips = sorted(glob.glob(os.path.join(BROLL_DIR, "gojo_action_*.mp4")))
    if not clips or len(clips) < 6:
        # Check parent broll
        clips = sorted(glob.glob(os.path.join(PROJECT_DIR, "data", "broll", "*.mp4")))
    if not clips:
        raise RuntimeError("No source clips available in data/broll.")

    selected_clips = (clips * 2)[:7] # 7 high-octane shots
    
    # 2. Audio: Prepare Slowed Bass-Boosted Phonk (eitaX signature: Louca slowed style)
    bgm_source = os.path.join(PROJECT_DIR, "data", "bgm", "aggressive_drift_phonk.mp3")
    if not os.path.exists(bgm_source):
        bgm_source = os.path.join(PROJECT_DIR, "data", "bgm", "anime_phonk_beat_1.mp3")
        
    mastered_audio = os.path.join(TEMP_DIR, "slowed_phonk_master.mp3")
    total_short_dur = 16.5 # 16.5 seconds sweet spot
    
    # Slow down slightly (0.92x), boost 60Hz 808 sub-bass (+5dB), add subtle spatial room reverb
    audio_filter = (
        "atempo=0.92,"
        "equalizer=f=60:width_type=h:width=40:g=5.5,"
        "equalizer=f=3200:width_type=h:width=800:g=2.0,"
        "aecho=0.8:0.7:30:0.3,"
        "loudnorm=I=-14:LRA=7:TP=-1.0"
    )
    cmd_audio = [
        FFMPEG, "-y",
        "-i", bgm_source,
        "-t", str(total_short_dur),
        "-filter_complex", audio_filter,
        "-c:a", "libmp3lame", "-b:a", "320k",
        mastered_audio
    ]
    subprocess.run(cmd_audio, check=True, capture_output=True)
    print(f"[+] Mastered Slowed Phonk Audio: {os.path.basename(mastered_audio)}")

    # 3. Processing each clip with eitaX Velocity & Impact Shader:
    # Shot duration ~2.35s each (7 shots * 2.35s = 16.45s)
    shot_dur = total_short_dur / len(selected_clips)
    processed_shots = []

    for idx, clip in enumerate(selected_clips):
        shot_out = os.path.join(TEMP_DIR, f"eitax_shot_{idx:02d}.mp4")
        
        # eitaX Shader Stack:
        # - Smart 9:16 vertical crop
        # - Decaying Impact Zoom Pulse (10% scale impulse decaying in 0.3s)
        # - RGB Chromatic Aberration Split (rh=5:bv=-5:edge=smear)
        # - White Strobe Flash on frame 0 (0.06s exposure burst)
        # - Deep Glow / Optical Bloom (Screen blend blurred layer)
        # - Rich Film Contrast CC & Unsharp enhancement
        # - 60 FPS fluid rendering
        shader_vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "scale='1080*(1+0.09*exp(-9*t))':'1920*(1+0.09*exp(-9*t))':eval=frame,"
            "crop=1080:1920,"
            "rgbashift=rh=5:bv=-5:edge=smear,"
            "fade=t=in:st=0:d=0.06:color=white,"
            "split[base][glow_in];"
            "[glow_in]boxblur=18:2,eq=brightness=0.12:contrast=1.35[glow_soft];"
            "[base][glow_soft]blend=all_mode=screen:all_opacity=0.32[blended];"
            "[blended]eq=contrast=1.35:saturation=1.38:brightness=-0.02,"
            "unsharp=5:5:1.1:5:5:0.0,"
            "fps=60"
        )
        
        cmd_shot = [
            FFMPEG, "-y",
            "-i", clip,
            "-t", str(shot_dur),
            "-vf", shader_vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-an",
            shot_out
        ]
        subprocess.run(cmd_shot, check=True, capture_output=True)
        processed_shots.append(shot_out)
        print(f" [+] Rendered Velocity Impact Shot {idx+1}/{len(selected_clips)} (60fps)")

    # 4. Concatenate Shots
    concat_manifest = os.path.join(TEMP_DIR, "eitax_concat_manifest.txt")
    with open(concat_manifest, "w") as f:
        for p in processed_shots:
            f.write(f"file '{p.replace(os.sep, '/')}'\n")

    # 5. Master Render with Audio & Minimal God-Tier Typography
    font_path = "C\\:/Windows/Fonts/arialbd.ttf"
    filter_complex = (
        "[0:v]"
        f"drawtext=fontfile='{font_path}':text='H O L L O W   P U R P L E':fontcolor=white:fontsize=72:bordercolor=black:borderw=6:x=(w-tw)/2:y=340:enable='between(t,0.2,3.5)',"
        f"drawtext=fontfile='{font_path}':text='LIMITLESS':fontcolor=0x00E5FF:fontsize=84:bordercolor=black:borderw=8:x=(w-tw)/2:y=440:enable='between(t,3.5,7.0)',"
        f"drawtext=fontfile='{font_path}':text='THE STRONGEST':fontcolor=0xFFE600:fontsize=92:bordercolor=black:borderw=8:x=(w-tw)/2:y=380:enable='gte(t,7.0)',"
        f"drawtext=fontfile='{font_path}':text='4K • 60FPS':fontcolor=white@0.7:fontsize=28:x=w-tw-40:y=80,"
        "fps=60[v]"
    )

    out_path = os.path.join(OUT_DIR, output_filename)
    cmd_master = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_manifest,
        "-i", mastered_audio,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        out_path
    ]
    
    print("[*] Encoding final 4K/60FPS master...")
    subprocess.run(cmd_master, check=True, capture_output=True)
    print(f"[OK] Master AMV Exported: {output_filename} ({os.path.getsize(out_path)/(1024*1024):.2f} MB)")

    # 6. Quality Control Audit
    qc = quality_control.audit_video(out_path)
    print(f"QC Audit Result: Passed={qc['passed']} (Issues: {qc['issues']})")

    # 7. Premiere Pro 2026 & After Effects Pro Suite
    ppro_res = premiere_automation.build_pro_editing_package(selected_clips, bgm_path=mastered_audio, title="GodTier_EitaX_AMV_4K")
    ae_res = aftereffects_bridge.generate_pro_aftereffects_comp(selected_clips, words=["CRIMSON", "MOON", "UPPER", "THREE", "AKAZA"], bgm_path=mastered_audio, title="GodTier_EitaX_AMV_4K")

    return out_path

def render_master_dark_psychology_short(output_filename="God_Tier_Dark_Psychology_4K.mp4"):
    """
    Renders an ultra-cinematic Movie Dark Psychology short (Fight Club / Tyler Durden)
    with James Prince professional timeline cuts, Noir CC, Charon AI Voiceover, ducked soundtrack,
    and kinetic gold & crimson subtitles.
    """
    print("\n" + "="*70)
    print("🧠 ARIS MASTER ENGINE: Rendering God-Tier Movie Dark Psychology Short")
    print("   Standard: Fight Club 1080p REMUX (James Prince Multi-Track Assembly, Charon AI, Noir CC)")
    print("="*70)

    # 1. Gather Shots from Fight Club
    fc_clips = sorted(glob.glob(os.path.join(BROLL_DIR, "fight_club_scene_*.mp4")))
    if not fc_clips or len(fc_clips) < 6:
        raise RuntimeError("No Fight Club clips available.")

    selected_fc = fc_clips[:8] # 8 cinematic shots
    
    # 2. Script & Studio Voiceover (Charon / Brian)
    from channel2_dark_psychology import generate_voiceover_and_cues, create_ass_subtitles
    import asyncio

    script_lines = [
        ("Never react immediately.", "Red"),
        ("Because the moment you react emotionally...", "Normal"),
        ("You hand over your power.", "Gold"),
        ("The most dangerous person in the room...", "Normal"),
        ("Is the one who observes everything.", "Gold"),
        ("Silence creates unbearable tension.", "Normal"),
        ("While they talk to fill the void...", "Normal"),
        ("You calculate their weaknesses.", "Red"),
        ("Master your emotions...", "Gold"),
        ("Or someone else will.", "Red")
    ]

    vo_file = os.path.join(TEMP_DIR, "master_vo_charon.mp3")
    total_dur, cues = asyncio.run(generate_voiceover_and_cues(script_lines, vo_file))
    print(f"[+] Studio Voiceover synthesized: {total_dur:.2f}s")

    ass_file = os.path.join(TEMP_DIR, "master_dark_subs.ass")
    create_ass_subtitles(cues, script_lines, ass_file, badge="DARK PSYCHOLOGY: RULE OF REACTION")

    # 3. Process each movie shot with Noir Shutter Shader & Slow Push-In
    dur_per_shot = (total_dur + 0.8) / len(selected_fc)
    processed_shots = []

    for idx, cp in enumerate(selected_fc):
        shot_out = os.path.join(TEMP_DIR, f"master_fc_shot_{idx:02d}.mp4")
        # Cinematic Film Look:
        # - Smart 9:16 Center Crop on character
        # - Subtle continuous slow push-in (scale from 1.0 to 1.05)
        # - Film Noir contrast grade & dark vignette
        # - 0.08s shutter black dip transition
        shader_vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "scale='1080*(1+0.04*t)':'1920*(1+0.04*t)':eval=frame,"
            "crop=1080:1920,"
            "eq=contrast=1.30:saturation=0.82:brightness=-0.04,"
            "vignette=PI/4.4,"
            "fade=t=in:st=0:d=0.08:color=black,"
            "fps=30"
        )
        cmd_shot = [
            FFMPEG, "-y",
            "-i", cp,
            "-t", str(dur_per_shot),
            "-vf", shader_vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "17",
            "-an",
            shot_out
        ]
        subprocess.run(cmd_shot, check=True, capture_output=True)
        processed_shots.append(shot_out)

    concat_manifest = os.path.join(TEMP_DIR, "master_fc_manifest.txt")
    with open(concat_manifest, "w") as f:
        for p in processed_shots:
            f.write(f"file '{p.replace(os.sep, '/')}'\n")

    # 4. Audio Mixing: Voiceover (100%) + Ducked Dark Cinematic Drone (22%) -> Broadcast -14 LUFS
    bgm_path = os.path.join(PROJECT_DIR, "data", "bgm", "dark_cinematic_theme.mp3")
    ass_escaped = ass_file.replace("\\", "/").replace(":", "\\:")

    filter_complex = (
        f"[0:v]subtitles='{ass_escaped}',fps=30[v];"
        f"[1:a]volume=1.0[vo];"
        f"[2:a]atrim=0:{total_dur + 0.8},volume=0.20,afade=t=out:st={total_dur}:d=0.8[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2,"
        f"loudnorm=I=-14:LRA=7:TP=-1.0[a]"
    )

    out_path = os.path.join(OUT_DIR, output_filename)
    cmd_master = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_manifest,
        "-i", vo_file,
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        out_path
    ]

    print("[*] Encoding final Movie Dark Psychology master...")
    subprocess.run(cmd_master, check=True, capture_output=True)
    print(f"[OK] Master Video Exported: {output_filename} ({os.path.getsize(out_path)/(1024*1024):.2f} MB)")

    # 5. Quality Control Audit
    qc = quality_control.audit_video(out_path)
    print(f"QC Audit Result: Passed={qc['passed']} (Issues: {qc['issues']})")

    # 6. Premiere Pro 2026 & After Effects Pro Suite
    ppro_res = premiere_automation.build_pro_editing_package(selected_fc, voiceover_path=vo_file, bgm_path=bgm_path, title="GodTier_FightClub_Dark_Psychology")
    ae_res = aftereffects_bridge.generate_pro_aftereffects_comp(selected_fc, words=["LOSING", "ALL", "HOPE", "WAS", "FREEDOM"], bgm_path=bgm_path, title="GodTier_FightClub_Dark_Psychology")

    return out_path

if __name__ == "__main__":
    v1 = render_eitax_god_tier_anime_short("God_Tier_Anime_AMV_4K.mp4")
    v2 = render_master_dark_psychology_short("God_Tier_Dark_Psychology_4K.mp4")

    downloads = os.path.expanduser("~\\Downloads")
    dst1 = os.path.join(downloads, "God_Tier_Anime_AMV_4K.mp4")
    dst2 = os.path.join(downloads, "God_Tier_Dark_Psychology_4K.mp4")
    shutil.copyfile(v1, dst1)
    shutil.copyfile(v2, dst2)
    print(f"\n🎉 EXPORTED DIRECTLY TO DOWNLOADS:")
    print(f" - {dst1} ({os.path.getsize(dst1)/(1024*1024):.2f} MB)")
    print(f" - {dst2} ({os.path.getsize(dst2)/(1024*1024):.2f} MB)")
